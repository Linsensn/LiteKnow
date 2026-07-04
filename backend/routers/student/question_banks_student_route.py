from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.database import get_db
from utils.deps import get_current_user
from services.question_bank_service import qb_service

router = APIRouter(prefix="/question-banks", tags=["Student - Question Banks"])

@router.post("")
async def create_my_question_bank(
    bank_in: dict = Body(..., description="题库创建信息"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    [学生端] 创建属于自己的专属题库
    """
    return await qb_service.create_bank(db=db, current_user=current_student, bank_in=bank_in)

@router.get("")
async def list_my_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    [学生端] 仅查询当前学生创建的题库
    """
    return await qb_service.get_banks(db=db, current_user=current_student, keyword=keyword, page=page, page_size=page_size)

@router.delete("/bulk")
async def student_bulk_delete_question_banks(
    bank_ids: List[int] = Body(..., embed=True, description="要删除的题库ID列表"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    [学生端] 批量删除自己名下的题库 (Service层会通过 id 校验越权操作)
    """
    await qb_service.bulk_delete(db=db, current_user=current_student, bank_ids=bank_ids)
    return {"message": "批量删除题库成功"}