# backend/routers/admin/attachments_admin_route.py
from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from config.database import get_db
from utils.deps import get_admin_user
from utils.response import success
from schemas.common import ResponseModel, PageResult
from schemas.attachment_schema import AttachmentResponse, AttachmentUpdate
from services.attachment_service import att_service

router = APIRouter(prefix="/attachments", tags=["Admin/attachments"])


# ==================== 查询 ====================

@router.get("", summary="管理员分页查询全站附件", response_model=ResponseModel[PageResult[AttachmentResponse]])
async def admin_get_all_attachments(
    file_type: Optional[str] = Query(None, description="按类型检索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    data = await att_service.get_attachment_page(
        db, user_id=None, file_type=file_type,
        page=page, page_size=page_size
    )
    data.list = [AttachmentResponse.model_validate(item) for item in data.list]
    return success(data=data)


@router.get("/filter", summary="多条件搜索附件", response_model=ResponseModel[PageResult[AttachmentResponse]])
async def admin_filter_attachments(
    user_id: Optional[int] = Query(None, description="按用户ID筛选"),
    file_type: Optional[str] = Query(None, description="按文件类型筛选"),
    keyword: Optional[str] = Query(None, description="OCR内容模糊搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    data = await att_service.get_attachments_filter(
        db, user_id=user_id, file_type=file_type, keyword=keyword,
        page=page, page_size=page_size
    )
    data.list = [AttachmentResponse.model_validate(item) for item in data.list]
    return success(data=data)


@router.get("/{attachment_id}", summary="查询附件详情", response_model=ResponseModel[AttachmentResponse])
async def admin_get_attachment(
    attachment_id: int = Path(..., description="附件ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    attachment = await att_service.get_attachment(db, attachment_id=attachment_id)
    return success(data=AttachmentResponse.model_validate(attachment))


@router.get("/statistics", summary="附件统计（按文件类型分组）")
async def admin_attachment_statistics(
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    stats = await att_service.get_attachment_statistics(db)
    return success(data=stats)


# ==================== 导出导入 ====================

@router.get("/export", summary="导出全站附件")
async def admin_export_attachments(
    user_id: Optional[int] = Query(None, description="按用户筛选"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    data = await att_service.export_attachments(db, user_id=user_id)
    return success(data=data)


@router.post("/import", summary="批量导入附件")
async def admin_import_attachments(
    attachments: List[dict] = Body(..., description="附件数据列表"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    count = await att_service.import_attachments(db, objs_in=attachments)
    return success(data={"import_count": count}, message=f"成功导入 {count} 个附件")


# ==================== 更新 ====================

@router.put("/{attachment_id}", summary="编辑附件信息")
async def admin_update_attachment(
    attachment_id: int = Path(..., description="附件ID"),
    update_data: AttachmentUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    await att_service.update_attachment(db, attachment_id=attachment_id, update_data=update_data)
    attachment = await att_service.get_attachment(db, attachment_id=attachment_id)
    return success(data=AttachmentResponse.model_validate(attachment), message="附件更新成功")


# ==================== 删除 ====================

@router.delete("/batch", summary="批量删除附件")
async def admin_batch_delete_attachments(
    ids: List[int] = Body(..., embed=True, description="附件ID列表"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    count = await att_service.batch_delete_attachments(db, ids=ids)
    return success(data={"deleted_count": count}, message=f"成功删除 {count} 个附件")


@router.delete("/{attachment_id}", summary="管理员强制删除附件")
async def admin_force_delete_attachment(
    attachment_id: int = Path(..., description="附件ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    await att_service.delete_attachment(db, attachment_id=attachment_id, user_id=None)
    return success(message="违规附件已强制删除")