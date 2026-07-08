# backend/utils/ocr_client.py
import logging
import subprocess
import tempfile
import os
import io
import pandas as pd
import docx
import fitz
from bs4 import BeautifulSoup
from fastapi import UploadFile
from paddleocr import PaddleOCR

logger = logging.getLogger("liteknow.ocr")

# 全局初始化 PaddleOCR 实例
# use_angle_cls=True 支持自动纠正图像倾斜/倒置，lang='ch' 支持中英文混合
ocr_engine = PaddleOCR(use_angle_cls=True, lang='ch')

async def parse_file_content(file: UploadFile) -> str:
    """
    统一的文件解析入口
    """
    file_ext = file.filename.split('.')[-1].lower()
    file_bytes = await file.read()
    try:
        if file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp']:
            return _extract_text_from_image(file_bytes)
        elif file_ext in ['doc', 'docx']:
            return _extract_text_from_word(file_bytes, file_ext)
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
        
        # 优化：仅针对宽度极小的图做放大
        if w < 1500:
            img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
            h, w = img.shape[:2]
            print(f"DEBUG: 放大后尺寸 {w} x {h} 像素")

        all_texts = []
        step = 800
        overlap = 50
        
        if h <= step:
            result = ocr_engine.ocr(img)
            if result and result[0]:
                all_texts.extend([line[1][0] for line in result[0]])
        else:
            for y in range(0, h, step - overlap):
                y_end = min(h, y + step)
                crop_img = img[y:y_end, :]
                print(f"DEBUG: 正在识别切片 y={y}~{y_end}，形状={crop_img.shape}")
                
                result = ocr_engine.ocr(crop_img)
                if result and result[0]:
                    all_texts.extend([line[1][0] for line in result[0]])
            
        if all_texts:
            print(f"DEBUG: 识别成功，共提取到 {len(all_texts)} 个文本块！")
            return "\n".join(all_texts)
        else:
            print("DEBUG: 依然未能识别到任何文字。")
            return ""
            
    except Exception as e:
        logger.error(f"本地 OCR 识别失败: {str(e)}")
        return ""

def _extract_text_from_word(file_bytes: bytes, file_ext: str) -> str:
    """
    区分 .doc 和 .docx 两种格式进行解析
    """
    # 1. 如果是新版 .docx
    if file_ext == 'docx':
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except Exception as e:
            logger.error(f"docx解析失败: {str(e)}")
            return ""

    # 2. 如果是旧版 .doc
    elif file_ext == 'doc':
        try:
            # 写入临时文件
            with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as tmp_file:
                tmp_file.write(file_bytes)
                tmp_path = tmp_file.name
            
            # 调用 antiword 提取
            result = subprocess.run(
                ['antiword', tmp_path], 
                capture_output=True, 
                text=True, 
                check=False
            )

            if "HTML" in result.stderr or "HTML" in result.stdout:
                try:
                    logger.info("检测到 HTML 格式伪装，正在启动 BeautifulSoup 兜底解析...")
                    soup = BeautifulSoup(file_bytes, 'html.parser')
                    text = soup.get_text(separator='\n')
                    return text
                except Exception as html_e:
                    logger.error(f"HTML 兜底解析也失败了: {str(html_e)}")
                    # 这里不要 return，继续往下走，看看是不是其他错误
            
            # 如果 antiword 确实解析失败但又不是 HTML
            if result.returncode != 0:
                logger.error(f"antiword 解析 .doc 失败！退出码: {result.returncode}, 错误信息: {result.stderr}")
                return ""
            
            # 如果 stdout 提取出来是空的
            if not result.stdout.strip():
                logger.warning("antiword 解析成功，但提取出的文本为空")
                return ""

            return result.stdout
            
        except Exception as e:
            logger.error(f".doc 解析失败: {str(e)}")
            return ""
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            
    return ""

async def _extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        
        if len(text) > 20:
            full_text += text + "\n"
        else:
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            ocr_text = _extract_text_from_image(img_bytes)
            full_text += ocr_text + "\n"
            
    doc.close()
    return full_text

async def parse_local_file(file_path: str, original_filename: str) -> str:
    file_ext = original_filename.split('.')[-1].lower()
    
    try:
        if file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp']:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            return _extract_text_from_image(file_bytes)
            
        elif file_ext in ['txt', 'md', 'csv']:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
                
        elif file_ext in ['doc', 'docx']:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            return _extract_text_from_word(file_bytes, file_ext)
            
        elif file_ext in ['xls', 'xlsx']:
            df = pd.read_excel(file_path)
            return df.to_csv(index=False) 
            
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