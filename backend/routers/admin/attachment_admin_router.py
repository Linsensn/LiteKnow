# backend/routers/admin/attachments_admin_route.py
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from config.database import get_db
from utils.deps import get_admin_user
from utils.response import success
from schemas.common import ResponseModel, PageResult
from schemas.attachment_schema import AttachmentResponse
from services.attachment_service import att_service

router = APIRouter(prefix="/attachments", tags=["Admin - 资源审计"])


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
    return success(data=data)


@router.delete("/{attachment_id}", summary="管理员强制删除附件")
async def admin_force_delete_attachment(
    attachment_id: int = Path(..., description="附件ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    await att_service.delete_attachment(db, attachment_id=attachment_id, user_id=None)
    return success(message="违规附件已强制删除")