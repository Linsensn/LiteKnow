# backend/utils/ocr_client.py
import logging
import io
import mimetypes
import pandas as pd
import docx
import fitz
from fastapi import UploadFile
from rapidocr import RapidOCR

logger = logging.getLogger("liteknow.ocr")

# 全局初始化 RapidOCR 实例
ocr_engine = RapidOCR() 

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
            return _extract_text_from_image(file_bytes)
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

def _extract_text_from_image(image_bytes: bytes) -> str:
    if not image_bytes:
        return ""
    try:
        import cv2
        import numpy as np
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return ""
            
        h, w, _ = img.shape
        print(f"DEBUG: 原始图片尺寸 {w} x {h} 像素")
        
        # 1. 转为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        all_texts = []
        
        # 2. 调整切片参数
        step = 600
        overlap = 50
        
        if h <= step:
            # ✅ 新增关键步骤：Otsu 二值化处理（转成纯净的黑白图）
            binary_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            # 如果原图较短，我们适当放大一点，确保小字能被检测到
            if binary_img.shape[0] < 600:
                binary_img = cv2.resize(binary_img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
                
            output = ocr_engine(binary_img, text_score=0.3)
            result = getattr(output, 'result', None)
            if result:
                all_texts.extend([item[1] for item in result])
        else:
            # 循环切片识别
            for y in range(0, h, step - overlap):
                y_end = min(h, y + step)
                crop_img = gray[y:y_end, :]
                print(f"DEBUG: 正在识别切片 y={y}~{y_end}，形状={crop_img.shape}")
                
                # ✅ 新增关键步骤：Otsu 二值化处理
                binary_crop = cv2.threshold(crop_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                
                output = ocr_engine(binary_crop, text_score=0.3)
                result = getattr(output, 'result', None)
                
                if result is None and isinstance(output, (tuple, list)) and len(output) > 0:
                    result = output[0]
                    
                if result:
                    all_texts.extend([item[1] for item in result])
            
        # 3. 检查结果
        if all_texts:
            print(f"DEBUG: 识别成功，共提取到 {len(all_texts)} 个文本块！")
            return "\n".join(all_texts)
        else:
            print("DEBUG: 即使二值化处理并放大后，依然未能识别到任何文字。")
            return ""
            
    except Exception as e:
        logger.error(f"本地 OCR 识别失败: {str(e)}")
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
            # 注意：这里调用的是同步函数，去掉 await
            ocr_text = _extract_text_from_image(img_bytes)
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
            # 注意：这里调用的是同步函数，去掉 await
            return _extract_text_from_image(file_bytes)
            
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