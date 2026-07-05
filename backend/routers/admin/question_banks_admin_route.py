from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.database import get_db
from utils.deps import get_current_user, get_admin_user
from services.question_bank_service import qb_service
from utils.response import success

router = APIRouter(prefix="/question-banks", tags=["Admin - Question Banks"])

@router.get("")
async def admin_list_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    """
    [管理员端] 获取全量题库列表，无视创建者归属
    """
    result = await qb_service.get_banks(db=db, current_user=current_admin, keyword=keyword, page=page, page_size=page_size)
    return success(data=result, message="获取全局题库列表成功")

@router.delete("/bulk")
async def admin_bulk_delete_question_banks(
    bank_ids: List[int] = Body(..., embed=True, description="要强制删除的题库ID列表"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    """
    [管理员端] 批量强制删除违规或无效题库
    """
    await qb_service.bulk_delete(db=db, current_user=current_admin, bank_ids=bank_ids)
    return success(message="全局批量删除成功")