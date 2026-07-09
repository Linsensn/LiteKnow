# backend/services/message_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from utils.exceptions import CustomAPIException, ErrorCode
from crud.messages_crud import msg_crud
from crud.favorites_crud import favorite_crud
from schemas.message_schema import MessageCreate
from schemas.common import PageResult

class MessageService:

    # 1. 获取单条消息详情
    async def get_message(self, db: AsyncSession, message_id: int):
        message = await msg_crud.get(db, message_id=message_id)
        if not message:
           raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND)
        return message

    # 2. 获取指定会话的全部消息列表
    async def get_session_messages(self, db: AsyncSession, session_id: int):
        # 注：若需严格校验会话归属权，可在此处补充会话查询与用户ID比对逻辑
        return await msg_crud.get_by_session(db, session_id=session_id)

    # 3. 管理员分页查询全量消息
    async def get_message_page(
        self, db: AsyncSession, *, session_id: int = None,
        page: int, page_size: int
    ):
        skip = (page - 1) * page_size
        total = await msg_crud.count(db, session_id=session_id)
        items = await msg_crud.get_multi(
            db, session_id=session_id, skip=skip, limit=page_size
        )
        return PageResult(
            list=items,
            total=total,
            page=page,
            page_size=page_size
        )

    # 4. 创建单条消息
    async def create_message(self, db: AsyncSession, obj_in: MessageCreate):
        try:
            new_msg = await msg_crud.create(db, obj_in=obj_in.model_dump())
            db.commit()
            db.refresh(new_msg)
            return new_msg
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # 5. 删除消息
    async def delete_message(self, db: AsyncSession, message_id: int):
        message = await self.get_message(db, message_id=message_id)
        try:
            # 级联清理收藏夹中对应的摘要ID
            await favorite_crud.remove_content_ids_by_type(
                db, content_type="summary", content_ids=[message_id]
            )
            await msg_crud.delete(db, db_obj=message)
            db.commit()
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)


msg_service = MessageService()