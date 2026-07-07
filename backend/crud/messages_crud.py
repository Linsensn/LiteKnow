# backend/crud/messages_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc
from typing import List, Optional
from models.messages import Message


class CRUDMessage:

    # 1. 单条消息查询
    async def get(self, db: AsyncSession, message_id: int) -> Optional[Message]:
        stmt = select(Message).where(Message.id == message_id)
        result = db.execute(stmt)
        return result.scalars().first() 

    # 2. 按会话ID查询全部消息（按创建时间正序，还原对话时序）
    async def get_by_session(self, db: AsyncSession, session_id: int) -> List[Message]:
        stmt = select(Message).where(
            Message.session_id == session_id
        ).order_by(asc(Message.created_at))
        result = db.execute(stmt)
        return result.scalars().all()

    # 3. 管理员分页全量查询（支持按会话ID筛选）
    async def get_multi(
        self, db: AsyncSession, *, session_id: Optional[int] = None,
        skip: int = 0, limit: int = 20
    ) -> List[Message]:
        stmt = select(Message)
        if session_id:
            stmt = stmt.where(Message.session_id == session_id)
        stmt = stmt.order_by(desc(Message.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    # 4. 统计符合条件的总记录数（配合分页）
    async def count(self, db: AsyncSession, *, session_id: Optional[int] = None) -> int:
        stmt = select(func.count(Message.id))
        if session_id:
            stmt = stmt.where(Message.session_id == session_id)
        result = db.execute(stmt)
        return result.scalar_one()

    # 5. 新增单条消息
    async def create(self, db: AsyncSession, *, obj_in: dict) -> Message:
        db_obj = Message(**obj_in)
        db.add(db_obj)
        db.flush()
        return db_obj

    # 6. 物理删除消息
    async def delete(self, db: AsyncSession, *, db_obj: Message):
        db.delete(db_obj)
        db.flush()


msg_crud = CRUDMessage()