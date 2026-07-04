from fastapi import APIRouter, Depends, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from services.practice_session_service import ps_service

router = APIRouter(prefix="/practice-sessions", tags=["Student - Practice Sessions"])

@router.post("")
async def start_practice_session(
    bank_id: int = Body(..., description="要练习的题库ID"),
    mode: str = Body(..., description="练习模式：sequential(顺序), random(随机) 等"),
    question_ids: list[int] = Body(..., description="初始题号列表序列"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    [学生端] 发起一次新的练习会话，后端将根据 mode 打乱或初始化答题队列
    """
    return await ps_service.start_new_session(
        db=db, 
        user_id=current_student["id"], 
        bank_id=bank_id, 
        mode=mode, 
        question_ids=question_ids
    )

@router.get("/{session_id}")
async def get_practice_session_progress(
    session_id: int = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    [学生端] 恢复上次中断的练习进度，获取当前会话详情
    """
    return await ps_service.get_session_detail(
        db=db, session_id=session_id, user_id=current_student["id"]
    )