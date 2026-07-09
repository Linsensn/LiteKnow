from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from utils.deps import get_current_user
from utils.response import success 
from utils.exceptions import CustomAPIException,  ErrorCode
from utils.ocr_client import parse_file_content
from services.attachment_service import att_service 
from schemas.ai_quiz_schema import QuizGenerateFormDependency
from schemas.common import ResponseModel, PageResult
from services.ai_quiz_service import ai_quiz_service

router = APIRouter(prefix="/ai/quiz", tags=["Student/AI/智能测验"])

@router.post("/generate", summary="智能生成结构化测验", response_model=ResponseModel[dict])
async def create_smart_quiz(
    req: QuizGenerateFormDependency = Depends(), # 使用 Depends 注入表单类
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    content_parts = []
    
    if req.content and req.content.strip():
        content_parts.append(f"【用户补充说明】:\n{req.content.strip()}")

    # 直接通过 ID 去数据库读识别好的文本 
    if req.attachment_ids:
        for att_id in req.attachment_ids:
            att = await att_service.get_attachment_by_id(db, att_id=att_id, user_id=current_student.id)
            
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

    result = await ai_quiz_service.generate_and_save_quiz(
        db=db,
        user_id=current_student.id, 
        session_id=req.session_id,
        bank_name=req.bank_name,
        user_content=final_user_content,
        model_name=req.model_name,
        question_count=req.question_count,
        difficulty=req.difficulty,
        question_types=req.question_types,
        target_bank_id=req.target_bank_id 
    )
    
    return success(data=result, message="智能测验生成并入库成功")