# backend/utils/ocr_client.py
import httpx
import logging
import io
from fastapi import UploadFile
import fitz 
import docx
import mimetypes
import pandas as pd

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

async def parse_local_file(file_path: str, original_filename: str) -> str:
    """
    通过本地存储位置读取文件并进行文本解析/OCR
    """
    file_ext = original_filename.split('.')[-1].lower()
    
    try:
        # 1. 图片类：读取二进制流走 OCR
        if file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp']:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            content_type, _ = mimetypes.guess_type(original_filename)
            return await _extract_from_image_bytes(file_bytes, original_filename, content_type or "image/jpeg")
            
        # 2. 纯文本类：直接以 UTF-8 读取字符串 (txt, md, csv)
        elif file_ext in ['txt', 'md', 'csv']:
            # 注意：有时 Windows 用户上传的 txt 是 gbk 编码，如果遇到乱码可以考虑加个编码容错逻辑
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
                
        # 3. Word 文档
        elif file_ext in ['doc', 'docx']:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            return _extract_text_from_word(file_bytes)
            
        # 4. Excel 表格
        elif file_ext in ['xls', 'xlsx']:
            # 用 pandas 读取表格，并转化为纯文本 CSV 格式返回给大模型
            # 这样既保留了行列结构，大模型也能读懂
            df = pd.read_excel(file_path)
            # 将 DataFrame 转换为纯文本，index=False 代表不输出行号
            return df.to_csv(index=False) 
            
        # 5. PDF 文档
        elif file_ext == 'pdf':
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            return await _extract_text_from_pdf(file_bytes)
            
        else:
            logger.warning(f"不支持的解析格式: {file_ext}")
            return ""
            
    except Exception as e:
        logger.error(f"本地文件读取/解析失败 {file_path}: {str(e)}")
        return ""