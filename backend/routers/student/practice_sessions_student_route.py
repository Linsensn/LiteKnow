from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from services.practice_session_service import ps_service
from utils.response import success
from schemas.practice_session_schemas import PracticeSessionCreate, PracticeSessionOut

router = APIRouter(prefix="/practice-sessions", tags=["Student - Practice Sessions"])

@router.post("")
async def start_practice_session(
    data: PracticeSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 发起一次新的练习会话"""
    result = await ps_service.start_new_session(
        db=db, 
        user_id=current_student["id"], 
        bank_id=data.bank_id, 
        mode=data.mode, 
        question_ids=data.question_ids
    )
    return success(data=PracticeSessionOut.model_validate(result).model_dump(), message="练习会话创建成功")

@router.get("/{session_id}")
async def get_practice_session_progress(
    session_id: int = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 恢复上次中断的练习进度"""
    result = await ps_service.get_session_detail(
        db=db, session_id=session_id, user_id=current_student["id"]
    )
    return success(data=PracticeSessionOut.model_validate(result).model_dump(), message="获取练习进度成功")