# backend/routers/admin/messages_admin_route.py
from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from config.database import get_db
from utils.deps import get_admin_user
from utils.response import success
from services.message_service import msg_service
from schemas.common import ResponseModel, PageResult
from schemas.message_schema import MessageResponse, MessageUpdate

router = APIRouter(prefix="/messages", tags=["Admin/messages"])


# ==================== 查询 ====================

@router.get("", summary="管理员分页查询全站消息", response_model=ResponseModel[PageResult[MessageResponse]])
async def admin_list_messages(
    session_id: Optional[int] = Query(None, description="按会话ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    data = await msg_service.get_message_page(
        db, session_id=session_id, page=page, page_size=page_size
    )
    data.list = [MessageResponse.model_validate(item) for item in data.list]
    return success(data=data)


@router.get("/filter", summary="多条件组合搜索消息", response_model=ResponseModel[PageResult[MessageResponse]])
async def admin_filter_messages(
    session_id: Optional[int] = Query(None, description="按会话ID筛选"),
    role: Optional[str] = Query(None, description="角色: user/assistant"),
    content_type: Optional[str] = Query(None, description="内容类型: text/mixed"),
    keyword: Optional[str] = Query(None, description="内容模糊搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    data = await msg_service.get_messages_filter(
        db, session_id=session_id, role=role,
        content_type=content_type, keyword=keyword,
        page=page, page_size=page_size
    )
    data.list = [MessageResponse.model_validate(item) for item in data.list]
    return success(data=data)


@router.get("/session/{session_id}", summary="管理员获取指定会话的全部消息")
async def admin_get_session_messages(
    session_id: int = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    items = await msg_service.get_session_messages(db, session_id=session_id)
    data = [MessageResponse.model_validate(item).model_dump() for item in items]
    return success(data=data)


@router.get("/{message_id}", summary="查询单条消息详情", response_model=ResponseModel[MessageResponse])
async def admin_get_message(
    message_id: int = Path(..., description="消息ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    message = await msg_service.get_message(db, message_id=message_id)
    return success(data=MessageResponse.model_validate(message))


@router.get("/statistics/{session_id}", summary="按会话统计消息概况")
async def admin_session_statistics(
    session_id: int = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    stats = await msg_service.get_session_statistics(db, session_id=session_id)
    return success(data=stats)


# ==================== 导出导入 ====================

@router.get("/export/{session_id}", summary="导出会话消息")
async def admin_export_messages(
    session_id: int = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    data = await msg_service.export_session_messages(db, session_id=session_id)
    return success(data=data)


@router.post("/import/{session_id}", summary="导入消息到会话")
async def admin_import_messages(
    session_id: int = Path(..., description="会话ID"),
    messages: List[dict] = Body(..., description="消息数据列表"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    count = await msg_service.import_session_messages(db, session_id=session_id, messages_data=messages)
    return success(data={"import_count": count}, message=f"成功导入 {count} 条消息")


# ==================== 更新 ====================

@router.put("/{message_id}", summary="编辑消息内容")
async def admin_update_message(
    message_id: int = Path(..., description="消息ID"),
    update_data: MessageUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    updated = await msg_service.update_message(db, message_id=message_id, update_data=update_data)
    return success(data=MessageResponse.model_validate(updated), message="消息更新成功")


# ==================== 删除 ====================

@router.delete("/batch", summary="批量删除消息")
async def admin_batch_delete_messages(
    ids: List[int] = Body(..., embed=True, description="消息ID列表"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    count = await msg_service.batch_delete_messages(db, ids=ids)
    return success(data={"deleted_count": count}, message=f"成功删除 {count} 条消息")


@router.delete("/{message_id}", summary="管理员强制删除消息")
async def admin_delete_message(
    message_id: int = Path(..., description="消息ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    await msg_service.delete_message(db, message_id=message_id)
    return success(message="违规消息已强制删除")