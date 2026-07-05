from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_admin_user
from services.question_bank_service import qb_service
from utils.response import success
from schemas.question_bank_schemas import QuestionBankOut, BulkDeleteIn

router = APIRouter(prefix="/admin/question-banks", tags=["Admin - Question Banks"])

@router.get("")
async def admin_list_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    """[管理员端] 获取全量题库列表"""
    result = await qb_service.get_banks(db=db, current_user=current_admin, keyword=keyword, page=page, page_size=page_size)
    items_data = [QuestionBankOut.model_validate(item).model_dump() for item in result["items"]]
    return success(data={"total": result["total"], "items": items_data}, message="获取全局题库列表成功")

@router.delete("/bulk")
async def admin_bulk_delete_question_banks(
    data: BulkDeleteIn,
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    """[管理员端] 批量强制删除题库"""
    await qb_service.bulk_delete(db=db, current_user=current_admin, bank_ids=data.bank_ids)
    return success(message="全局批量删除成功")