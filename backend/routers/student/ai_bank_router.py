# backend/routers/student/ai_bank_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from config.database import get_db
from utils.deps import get_current_user
from utils.exceptions import CustomAPIException, ErrorCode
from utils.response import success

from schemas.ai_bank_schema import BankParseRequest, BankParseResponse
from services.ai_bank_service import ai_bank_service
from services.attachment_service import att_service

logger = logging.getLogger("liteknow.ai_bank")
router = APIRouter(prefix="/ai/bank", tags=["Student/AI/智能题库"])

@router.post("/parse", response_model=BankParseResponse, summary="提取文本/图片生成结构化题库")
async def parse_text_to_bank(
    req: BankParseRequest,
    db: AsyncSession = Depends(get_db), # 🌟 对齐组长：使用 AsyncSession
    current_student = Depends(get_current_user)
):
    user_id = current_student.id
    content_parts = []
    
    if req.content and req.content.strip():
        content_parts.append(f"【用户文本说明】:\n{req.content.strip()}")

    # 🌟 对齐组长：使用解析后的属性获取真实 list
    parsed_ids = req.parsed_attachment_ids
    if parsed_ids:
        for att_id in parsed_ids:
            att = await att_service.get_attachment_by_id(db, att_id=att_id, user_id=user_id)
            if att and att.extracted_text and att.extracted_text.strip():
                content_parts.append(f"【附件提取内容】:\n{att.extracted_text}")
            else:
                logger.warning(f"附件 {att_id} 不存在或未提取到有效文本")

    if not content_parts:
        raise CustomAPIException(
            code=ErrorCode.FILE_OR_IMAGE_VALIDATION_ERROR, 
            message="请提供有效的文本内容或上传能识别出文字的图片/文件"
        )
        
    final_user_content = "\n\n".join(content_parts)
    
    result = await ai_bank_service.parse_and_save_bank(
        db=db, 
        user_id=user_id, 
        bank_name=req.bank_name,
        model_name=req.model_name, # 🌟 往下层透传模型名
        final_content=final_user_content
    )
    
    return result