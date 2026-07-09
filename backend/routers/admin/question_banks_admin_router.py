import logging
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from utils.deps import get_admin_user
from services.question_bank_service import qb_service
from utils.response import success

# 引入 User 模型
from models.users import User
from schemas.common import ResponseModel, PageResult
from schemas.question_bank_schemas import QuestionBankOut, QuestionBankUpdate, BulkDeleteIn

audit_logger = logging.getLogger("liteknow.audit")

# 👇 修复 2：去掉多余的 /admin 前缀，解决 404 路由嵌套双重 /admin 问题
router = APIRouter(prefix="/question-banks", tags=["Admin/Question Banks"])

@router.get("", response_model=ResponseModel[PageResult[QuestionBankOut]], summary="管理员分页搜索全局题库")
async def admin_list_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述", examples=["MQTT通信与ThingsBoard平台配置"]),
    sort_by: str = Query("desc", description="排序", examples=["desc"]),
    page: int = Query(1, ge=1, description="页码", examples=[1]),
    page_size: int = Query(20, ge=1, le=100, description="每页数量", examples=[20]),
    db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_admin_user)
):
    """管理员分页查看全局题库列表，支持关键字搜索和排序"""
    # 👇 修复 1：显式声明这是管理员视角，跳过用户ID过滤 (解决越权Bug)
    result = await qb_service.get_banks(db=db, current_user=current_admin, keyword=keyword, page=page, page_size=page_size, sort_by=sort_by, is_admin_mode=True)
    items_data = [QuestionBankOut.model_validate(item) for item in result["items"]]
    
    page_data = PageResult(
        list=items_data, 
        total=result["total"], 
        page=page, 
        page_size=page_size
    )
    return success(data=page_data, message="获取全局题库列表成功")

@router.get("/{bank_id}", response_model=ResponseModel[QuestionBankOut], summary="管理员获取单个题库详情")
async def admin_get_question_bank_detail(
    bank_id: int = Path(..., description="题库ID", examples=[5012]), db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_admin_user)
):
    """根据题库ID获取全局题库的详细信息"""
    bank = await qb_service.get_bank_detail(db=db, current_user=current_admin, bank_id=bank_id)
    return success(data=QuestionBankOut.model_validate(bank))

@router.patch("/{bank_id}", response_model=ResponseModel[dict], summary="管理员强制更新题库信息")
async def admin_update_question_bank(
    data: QuestionBankUpdate, bank_id: int = Path(..., description="题库ID", examples=[5012]), db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_admin_user)
):
    """管理员直接修改指定题库的属性（无视归属校验）"""
    updated_count = await qb_service.update_bank(db=db, current_user=current_admin, bank_id=bank_id, update_data=data.model_dump())
    audit_logger.info(f"Admin {current_admin.id} force updated bank {bank_id}")
    return success(message=f"全局题库信息更新成功，影响 {updated_count or 0} 个")

@router.delete("/bulk", response_model=ResponseModel[dict], summary="管理员批量删除题库")
async def admin_bulk_delete_question_banks(
    data: BulkDeleteIn, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_admin_user)
):
    """批量删除指定的题库，用于管理员强制清理"""
    # 👇 修复 1：显式声明这是管理员视角，允许越权删除 (解决越权Bug)
    deleted_count = await qb_service.bulk_delete(db=db, current_user=current_admin, bank_ids=data.bank_ids, is_admin_mode=True)
    audit_logger.warning(f"Admin {current_admin.id} force batch deleted banks {data.bank_ids}")
    return success(message=f"全局批量删除成功，共删除 {deleted_count or 0} 个题库")

@router.delete("/{bank_id}", response_model=ResponseModel[dict], summary="管理员删除单个题库")
async def admin_delete_single_bank(
    bank_id: int = Path(..., description="题库ID", examples=[5012]), db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_admin_user)
):
    """删除指定ID的题库，内部复用批量删除逻辑"""
    # 👇 修复 1：显式声明这是管理员视角，允许越权删除 (解决越权Bug)
    deleted_count = await qb_service.bulk_delete(db=db, current_user=current_admin, bank_ids=[bank_id], is_admin_mode=True)
    audit_logger.warning(f"Admin {current_admin.id} force deleted bank {bank_id}")
    return success(message=f"全局题库删除成功，共删除 {deleted_count or 0} 个题库")