# backend/services/message_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from utils.exceptions import CustomAPIException, ErrorCode
from crud.messages_crud import msg_crud
from crud.favorites_crud import favorite_crud
from schemas.message_schema import MessageCreate, MessageUpdate
from schemas.common import PageResult


class MessageService:

    # ==================== 查询 ====================

    async def get_message(self, db: AsyncSession, message_id: int):
        """单条查询"""
        message = await msg_crud.get(db, message_id=message_id)
        if not message:
           raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND)
        return message

    async def get_session_messages(self, db: AsyncSession, session_id: int):
        """按会话ID获取全部消息"""
        return await msg_crud.get_by_session(db, session_id=session_id)

    async def get_message_page(
        self, db: AsyncSession, *, session_id: int = None,
        page: int, page_size: int
    ):
        """管理员分页查询全量消息"""
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

    async def get_messages_filter(
        self, db: AsyncSession, *, session_id: Optional[int] = None,
        role: Optional[str] = None, content_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1, page_size: int = 20
    ):
        """多条件组合 + 模糊分页查询"""
        skip = (page - 1) * page_size
        items, total = await msg_crud.get_multi_filter(
            db, session_id=session_id, role=role,
            content_type=content_type, keyword=keyword,
            skip=skip, limit=page_size
        )
        return PageResult(
            list=items,
            total=total,
            page=page,
            page_size=page_size
        )

    # ==================== 统计 ====================

    async def get_session_statistics(self, db: AsyncSession, session_id: int) -> dict:
        """按会话统计消息概况"""
        return await msg_crud.get_session_statistics(db, session_id=session_id)

    # ==================== 新增 ====================

    async def create_message(self, db: AsyncSession, obj_in: MessageCreate):
        """创建单条消息"""
        try:
            new_msg = await msg_crud.create(db, obj_in=obj_in.model_dump())
            db.commit()
            db.refresh(new_msg)
            return new_msg
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # ==================== 更新 ====================

    async def update_message(
        self, db: AsyncSession, message_id: int, update_data: MessageUpdate
    ):
        """编辑单条消息"""
        message = await self.get_message(db, message_id=message_id)
        try:
            updated = await msg_crud.update(
                db, db_obj=message, update_data=update_data.model_dump(exclude_none=True)
            )
            db.commit()
            return updated
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # ==================== 删除 ====================

    async def delete_message(self, db: AsyncSession, message_id: int):
        """删除单条消息（级联清理收藏夹）"""
        message = await self.get_message(db, message_id=message_id)
        try:
            await favorite_crud.remove_content_ids_by_type(
                db, content_type="summary", content_ids=[message_id]
            )
            await msg_crud.delete(db, db_obj=message)
            db.commit()
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    async def batch_delete_messages(self, db: AsyncSession, ids: List[int]):
        """批量删除消息"""
        try:
            # 级联清理收藏夹
            await favorite_crud.remove_content_ids_by_type(
                db, content_type="summary", content_ids=ids
            )
            count = await msg_crud.delete_by_ids(db, ids=ids)
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # ==================== 导入导出 ====================

    async def export_session_messages(
        self, db: AsyncSession, session_id: int
    ) -> List[dict]:
        """导出会话消息"""
        return await msg_crud.export_by_session(db, session_id=session_id)

    async def import_session_messages(
        self, db: AsyncSession, session_id: int, messages_data: List[dict]
    ) -> int:
        """导入消息到会话"""
        try:
            count = await msg_crud.import_messages(
                db, session_id=session_id, messages_data=messages_data
            )
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)


msg_service = MessageService()