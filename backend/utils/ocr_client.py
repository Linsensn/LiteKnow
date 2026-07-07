# backend/utils/ocr_client.py
import httpx
import logging
import io
from fastapi import UploadFile
import fitz  # PyMuPDF
import docx

logger = logging.getLogger("liteknow.ocr")

async def parse_file_content(file: UploadFile) -> str:
    """
    统一的文件解析入口：
    1. 图片：直接发给 OCR 容器
    2. Word：直接提取文本
    3. PDF：先尝试直接提取文本，如果提取不到（扫描件），则将页面转为图片发给 OCR
    """
    file_ext = file.filename.split('.')[-1].lower()
    file_bytes = await file.read()

    try:
        if file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp']:
            return await _extract_from_image_bytes(file_bytes, file.filename, file.content_type)
            
        elif file_ext in ['doc', 'docx']:
            return _extract_text_from_word(file_bytes)
            
        elif file_ext == 'pdf':
            return await _extract_text_from_pdf(file_bytes)
            
        else:
            logger.warning(f"不支持的文件格式: {file_ext}")
            return ""
    except Exception as e:
        logger.error(f"文件解析失败 {file.filename}: {str(e)}")
        return ""

async def _extract_from_image_bytes(image_bytes: bytes, filename: str, content_type: str) -> str:
    """调用本地 RapidOCR 容器提取图片文字"""
    ocr_url = "http://ocr:9003/ocr"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ocr_url,
                files={"image": (filename, image_bytes, content_type)},
                timeout=20.0 
            )
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                text_lines = [item["text"] for item in result.get("data", [])]
                return "\n".join(text_lines)
    except Exception as e:
        logger.error(f"OCR 服务调用异常: {str(e)}")
    return ""

def _extract_text_from_word(file_bytes: bytes) -> str:
    """解析 Word 文档文本"""
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

async def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """解析 PDF，具备 OCR 降级能力"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        
        # 如果当前页能直接提取出较多文本，说明是数字版 PDF
        if len(text) > 20:
            full_text += text + "\n"
        else:
            # 如果提取不出文本，说明是扫描件，将当前页渲染为图片并调用 OCR
            pix = page.get_pixmap(dpi=150) # 设置 DPI 保证识别清晰度
            img_bytes = pix.tobytes("png")
            ocr_text = await _extract_from_image_bytes(img_bytes, f"page_{page_num}.png", "image/png")
            full_text += ocr_text + "\n"
            
    doc.close()
    return full_text