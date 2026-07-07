from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from utils.deps import get_current_user
from utils.response import success 

from schemas.ai_quiz_schema import QuizGenerateRequest
from schemas.common import ResponseModel, PageResult
from services.ai_quiz_service import ai_quiz_service

router = APIRouter(prefix="/ai/quiz", tags=["Student/AI/智能测验"])

@router.post("/generate", summary="智能生成结构化测验", response_model=ResponseModel[dict])
async def create_smart_quiz(
    req: QuizGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    接收课文要点，调用大模型生成带有解析与校验的选择题。
    生成的题目将直接自动归档进入该用户的专属题库中。
    """
    result = await ai_quiz_service.generate_and_save_quiz(
        db=db,
        user_id=current_student["id"],
        session_id=req.session_id,
        bank_name=req.bank_name,
        user_content=req.content
    )
    
    return success(data=result, message="智能测验生成并入库成功")