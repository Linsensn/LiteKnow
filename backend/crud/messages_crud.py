# backend/crud/messages_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc, delete, update
from typing import List, Optional, Tuple
from models.messages import Message


class CRUDMessage:

    # ==================== 新增 ====================

    async def create(self, db: AsyncSession, *, obj_in: dict) -> Message:
        """单条新增"""
        db_obj = Message(**obj_in)
        db.add(db_obj)
        db.flush()
        return db_obj

    async def create_multi(self, db: AsyncSession, *, objs_in: List[dict]) -> int:
        """批量新增"""
        db_objs = [Message(**obj) for obj in objs_in]
        db.add_all(db_objs)
        db.flush()
        return len(db_objs)

    # ==================== 查询 ====================

    async def get(self, db: AsyncSession, message_id: int) -> Optional[Message]:
        """单条查询"""
        stmt = select(Message).where(Message.id == message_id)
        result = db.execute(stmt)
        return result.scalars().first()

    async def get_by_ids(self, db: AsyncSession, *, ids: List[int]) -> List[Message]:
        """批量查询：按 ID 列表"""
        stmt = select(Message).where(Message.id.in_(ids))
        result = db.execute(stmt)
        return result.scalars().all()

    async def get_by_session(self, db: AsyncSession, session_id: int) -> List[Message]:
        """按会话ID查询全部消息（按创建时间正序，还原对话时序）"""
        stmt = select(Message).where(
            Message.session_id == session_id
        ).order_by(asc(Message.created_at))
        result = db.execute(stmt)
        return result.scalars().all()

    async def get_multi(
        self, db: AsyncSession, *, session_id: Optional[int] = None,
        skip: int = 0, limit: int = 20
    ) -> List[Message]:
        """分页查询（支持按会话ID筛选）"""
        stmt = select(Message)
        if session_id:
            stmt = stmt.where(Message.session_id == session_id)
        stmt = stmt.order_by(desc(Message.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    async def get_multi_filter(
        self, db: AsyncSession, *, session_id: Optional[int] = None,
        role: Optional[str] = None, content_type: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[Message], int]:
        """多条件组合查询 + 模糊查询：支持按会话/角色/内容类型筛选、内容模糊搜索，返回(列表, 总数)"""
        stmt = select(Message)
        conditions = []
        if session_id is not None:
            conditions.append(Message.session_id == session_id)
        if role:
            conditions.append(Message.role == role)
        if content_type:
            conditions.append(Message.content_type == content_type)
        if keyword:
            conditions.append(Message.content.ilike(f"%{keyword}%"))

        if conditions:
            stmt = stmt.where(*conditions)

        # 总数
        count_stmt = select(func.count(Message.id)).select_from(Message)
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        count_res = db.execute(count_stmt)
        total = count_res.scalar() or 0

        stmt = stmt.order_by(desc(Message.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all(), total

    async def get_with_session(self, db: AsyncSession, message_id: int) -> Optional[Message]:
        """关联查询：通过 join 拉取 Session 信息（需 Message 模型定义 relationship）"""
        # 当前 Message 模型未定义 relationship，如需使用请先在 models/messages.py 中添加：
        #   session = relationship("Session", backref="messages")
        stmt = select(Message).where(Message.id == message_id)
        result = db.execute(stmt)
        return result.scalars().first()

    # ==================== 统计 ====================

    async def count(self, db: AsyncSession, *, session_id: Optional[int] = None) -> int:
        """统计符合条件的总记录数（配合分页）"""
        stmt = select(func.count(Message.id))
        if session_id:
            stmt = stmt.where(Message.session_id == session_id)
        result = db.execute(stmt)
        return result.scalar() or 0

    async def get_session_statistics(self, db: AsyncSession, session_id: int) -> dict:
        """聚合计算：按会话统计消息概况（总消息数、各角色数量）"""
        total_stmt = select(func.count(Message.id)).where(Message.session_id == session_id)
        total = db.execute(total_stmt).scalar() or 0

        role_stmt = select(
            Message.role, func.count(Message.id).label("count")
        ).where(
            Message.session_id == session_id
        ).group_by(Message.role)
        role_result = db.execute(role_stmt)
        role_counts = {row.role: row.count for row in role_result.all()}

        return {
            "session_id": session_id,
            "total": total,
            "role_counts": role_counts
        }

    # ==================== 更新 ====================

    async def update(self, db: AsyncSession, *, db_obj: Message, update_data: dict) -> Message:
        """单条更改"""
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    async def update_by_ids(self, db: AsyncSession, *, ids: List[int], update_data: dict) -> int:
        """批量更改"""
        if not update_data:
            return 0
        stmt = update(Message).where(Message.id.in_(ids)).values(**update_data)
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    # ==================== 删除 ====================

    async def delete(self, db: AsyncSession, *, db_obj: Message):
        """单条删除"""
        db.delete(db_obj)
        db.flush()

    async def delete_by_ids(self, db: AsyncSession, *, ids: List[int]) -> int:
        """批量删除"""
        stmt = delete(Message).where(Message.id.in_(ids))
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    async def delete_by_session(self, db: AsyncSession, session_id: int) -> int:
        """按会话ID批量删除（级联清理）"""
        stmt = delete(Message).where(Message.session_id == session_id)
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    # ==================== 导入导出 ====================

    async def export_by_session(self, db: AsyncSession, session_id: int) -> List[dict]:
        """数据导出：将会话下所有消息导出为字典列表"""
        messages = await self.get_by_session(db, session_id)
        return [
            {
                "id": m.id,
                "session_id": m.session_id,
                "role": m.role,
                "content_type": m.content_type,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in messages
        ]

    async def import_messages(
        self, db: AsyncSession, *, session_id: int, messages_data: List[dict]
    ) -> int:
        """数据导入：批量导入消息到指定会话"""
        objs_in = []
        for item in messages_data:
            obj = {
                "session_id": session_id,
                "role": item.get("role", "user"),
                "content_type": item.get("content_type", "text"),
                "content": item.get("content", "")
            }
            objs_in.append(obj)
        return await self.create_multi(db, objs_in=objs_in)


msg_crud = CRUDMessage()