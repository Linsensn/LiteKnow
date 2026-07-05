# backend/routers/student/messages_student_route.py
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from utils.response import success
from services.message_service import msg_service
from schemas.message_schema import MessageCreate, MessageResponse

router = APIRouter(prefix="/messages", tags=["Student - 对话消息"])


@router.get("/session/{session_id}", summary="获取指定会话的消息列表")
async def get_session_messages(
    session_id: int = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    items = await msg_service.get_session_messages(db, session_id=session_id)
    data = [MessageResponse.model_validate(item).model_dump() for item in items]
    return success(data=data)


@router.post("", summary="写入单条消息")
async def create_message(
    msg_in: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    new_msg = await msg_service.create_message(db, obj_in=msg_in)
    return success(
        data=MessageResponse.model_validate(new_msg).model_dump(),
        message="消息发送成功"
    )


@router.delete("/{message_id}", summary="删除单条消息")
async def delete_my_message(
    message_id: int = Path(..., description="消息ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    await msg_service.delete_message(db, message_id=message_id)
    return success(message="消息删除成功")