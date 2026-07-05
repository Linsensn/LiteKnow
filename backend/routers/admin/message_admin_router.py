# backend/routers/admin/messages_admin_route.py
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from config.database import get_db
from utils.deps import get_admin_user
from utils.response import success
from services.message_service import msg_service

router = APIRouter(prefix="/messages", tags=["Admin - 消息审计"])
 

@router.get("", summary="管理员分页查询全站消息")
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
    return success(data=data)


@router.get("/{message_id}", summary="查询单条消息详情")
async def admin_get_message(
    message_id: int = Path(..., description="消息ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    message = await msg_service.get_message(db, message_id=message_id)
    return success(data=message)


@router.delete("/{message_id}", summary="管理员强制删除消息")
async def admin_delete_message(
    message_id: int = Path(..., description="消息ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    await msg_service.delete_message(db, message_id=message_id)
    return success(message="违规消息已强制删除")