from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.database import get_db
# 假设你的 auth/deps 工具中区分了获取 admin 和 student 的方法
from utils.auth import get_current_admin 
from services.question_bank_service import qb_service

router = APIRouter(prefix="/question-banks", tags=["Admin - Question Banks"])

@router.get("")
async def admin_list_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """
    [管理员端] 获取全量题库列表，无视创建者归属
    """
    return await qb_service.get_banks(db=db, current_user=current_admin, keyword=keyword, page=page, page_size=page_size)

@router.delete("/bulk")
async def admin_bulk_delete_question_banks(
    bank_ids: List[int] = Body(..., embed=True, description="要强制删除的题库ID列表"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """
    [管理员端] 批量强制删除违规或无效题库
    """
    await qb_service.bulk_delete(db=db, current_user=current_admin, bank_ids=bank_ids)
    return {"message": "全局批量删除成功"}