import logging
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from utils.deps import get_admin_user
from services.question_bank_service import qb_service
from utils.response import success

from schemas.common import ResponseModel, PageResult
from schemas.question_bank_schemas import QuestionBankOut, QuestionBankUpdate, BulkDeleteIn

audit_logger = logging.getLogger("liteknow.audit")
router = APIRouter(prefix="/admin/question-banks", tags=["Admin - Question Banks"])

@router.get("", response_model=ResponseModel[PageResult[QuestionBankOut]])
async def admin_list_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述"),
    sort_by: str = Query("desc", description="排序"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db), current_admin: dict = Depends(get_admin_user)
):
    """[管理员] 获取全量题库列表"""
    result = await qb_service.get_banks(db=db, current_user=current_admin, keyword=keyword, page=page, page_size=page_size, sort_by=sort_by)
    items_data = [QuestionBankOut.model_validate(item).model_dump() for item in result["items"]]
    page_data = {"list": items_data, "total": result["total"], "page": page, "page_size": page_size}
    return success(data=page_data, message="获取全局题库列表成功")

@router.get("/{bank_id}", response_model=ResponseModel[QuestionBankOut])
async def admin_get_question_bank_detail(
    bank_id: int = Path(...), db: AsyncSession = Depends(get_db), current_admin: dict = Depends(get_admin_user)
):
    """[管理员] 查看任意题库详情"""
    bank = await qb_service.get_bank_detail(db=db, current_user=current_admin, bank_id=bank_id)
    return success(data=QuestionBankOut.model_validate(bank).model_dump())

@router.patch("/{bank_id}", response_model=ResponseModel[dict])
async def admin_update_question_bank(
    data: QuestionBankUpdate, bank_id: int = Path(...), db: AsyncSession = Depends(get_db), current_admin: dict = Depends(get_admin_user)
):
    """[管理员] 强制修改任意题库信息"""
    await qb_service.update_bank(db=db, current_user=current_admin, bank_id=bank_id, update_data=data.model_dump())
    audit_logger.info(f"Admin {current_admin['id']} force updated bank {bank_id}")
    return success(message="全局题库信息更新成功")

@router.delete("/bulk", response_model=ResponseModel[dict])
async def admin_bulk_delete_question_banks(
    data: BulkDeleteIn, db: AsyncSession = Depends(get_db), current_admin: dict = Depends(get_admin_user)
):
    """[管理员] 批量强制删除题库"""
    await qb_service.bulk_delete(db=db, current_user=current_admin, bank_ids=data.bank_ids)
    audit_logger.warning(f"Admin {current_admin['id']} force batch deleted banks {data.bank_ids}")
    return success(message="全局批量删除成功")

@router.delete("/{bank_id}", response_model=ResponseModel[dict])
async def admin_delete_single_bank(
    bank_id: int = Path(...), db: AsyncSession = Depends(get_db), current_admin: dict = Depends(get_admin_user)
):
    """[管理员] 单条强制删除题库"""
    await qb_service.bulk_delete(db=db, current_user=current_admin, bank_ids=[bank_id])
    audit_logger.warning(f"Admin {current_admin['id']} force deleted bank {bank_id}")
    return success(message="全局题库删除成功")