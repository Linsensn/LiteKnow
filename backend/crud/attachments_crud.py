# backend/crud/attachments_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, delete, update
from typing import List, Optional, Tuple
from models.attachments import Attachment


class CRUDAttachment:

    # ==================== 新增 ====================

    async def create_attachment(
        self, db: AsyncSession, *, user_id: int, file_type: str,
        file_url: str, extracted_text: Optional[str] = None,
        message_id: Optional[int] = None
    ) -> Attachment:
        """单条新增：带用户归属创建附件记录"""
        db_obj = Attachment(
            user_id=user_id,
            file_type=file_type,
            file_url=file_url,
            extracted_text=extracted_text,
            message_id=message_id
        )
        db.add(db_obj)
        db.flush()
        return db_obj

    async def create_with_owner(
        self, db: AsyncSession, *, user_id: int, file_type: str,
        file_url: str, extracted_text: Optional[str] = None,
        message_id: Optional[int] = None
    ) -> Attachment:
        """单条新增（create_attachment 别名）"""
        return await self.create_attachment(
            db, user_id=user_id, file_type=file_type, file_url=file_url,
            extracted_text=extracted_text, message_id=message_id
        )

    async def create_multi(
        self, db: AsyncSession, *, objs_in: List[dict]
    ) -> int:
        """批量新增"""
        db_objs = [Attachment(**obj) for obj in objs_in]
        db.add_all(db_objs)
        db.flush()
        return len(db_objs)

    # ==================== 查询 ====================

    async def get(self, db: AsyncSession, attachment_id: int) -> Optional[Attachment]:
        """单条查询：获取附件详情"""
        stmt = select(Attachment).where(Attachment.id == attachment_id)
        result = db.execute(stmt)
        return result.scalars().first()

    async def get_by_ids(
        self, db: AsyncSession, *, ids: List[int]
    ) -> List[Attachment]:
        """批量查询：按 ID 列表"""
        stmt = select(Attachment).where(Attachment.id.in_(ids))
        result = db.execute(stmt)
        return result.scalars().all()

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Attachment], int]:
        """按用户查询：分页返回用户的附件列表及总数"""
        stmt = select(Attachment).where(Attachment.user_id == user_id)
        count_stmt = select(func.count(Attachment.id)).where(Attachment.user_id == user_id)
        total = db.execute(count_stmt).scalar() or 0
        stmt = stmt.order_by(desc(Attachment.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all(), total

    async def get_by_message(
        self, db: AsyncSession, *, message_id: int
    ) -> List[Attachment]:
        """按消息ID查询：获取绑定的所有附件"""
        stmt = select(Attachment).where(Attachment.message_id == message_id)
        result = db.execute(stmt)
        return result.scalars().all()

    async def get_multi_attachments(
        self, db: AsyncSession, *, user_id: Optional[int] = None,
        file_type: Optional[str] = None, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Attachment], int]:
        """多条件组合分页查询：支持按用户、文件类型筛选，返回(列表, 总数)"""
        stmt = select(Attachment)
        conditions = []
        if user_id is not None:
            conditions.append(Attachment.user_id == user_id)
        if file_type:
            conditions.append(Attachment.file_type.ilike(f"%{file_type}%"))

        if conditions:
            stmt = stmt.where(*conditions)

        # 总数查询
        count_stmt = select(func.count(Attachment.id)).select_from(Attachment)
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        count_res = db.execute(count_stmt)
        total = count_res.scalar() or 0

        stmt = stmt.order_by(desc(Attachment.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all(), total

    async def get_multi_filter(
        self, db: AsyncSession, *, user_id: Optional[int] = None,
        file_type: Optional[str] = None, message_id: Optional[int] = None,
        keyword: Optional[str] = None, skip: int = 0, limit: int = 20,
        sort_by: str = "desc"
    ) -> Tuple[List[Attachment], int]:
        """多条件组合 + 模糊查询：支持对 extracted_text 模糊搜索，返回(列表, 总数)"""
        stmt = select(Attachment)
        conditions = []
        if user_id is not None:
            conditions.append(Attachment.user_id == user_id)
        if file_type:
            conditions.append(Attachment.file_type == file_type)
        if message_id is not None:
            conditions.append(Attachment.message_id == message_id)
        if keyword:
            conditions.append(Attachment.extracted_text.ilike(f"%{keyword}%"))

        if conditions:
            stmt = stmt.where(*conditions)

        count_stmt = select(func.count(Attachment.id)).select_from(Attachment)
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = db.execute(count_stmt).scalar() or 0

        order_col = desc(Attachment.created_at) if sort_by == "desc" else asc(Attachment.created_at)
        stmt = stmt.order_by(order_col).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all(), total

    # ==================== 统计 ====================

    async def count(
        self, db: AsyncSession, *, user_id: Optional[int] = None,
        file_type: Optional[str] = None
    ) -> int:
        """统计符合条件的总记录数（配合分页）"""
        stmt = select(func.count(Attachment.id))
        if user_id is not None:
            stmt = stmt.where(Attachment.user_id == user_id)
        if file_type:
            stmt = stmt.where(Attachment.file_type.ilike(f"%{file_type}%"))

        result = db.execute(stmt)
        return result.scalar() or 0

    async def get_statistics(
        self, db: AsyncSession, *, user_id: Optional[int] = None
    ) -> dict:
        """聚合计算：按 file_type 分组统计附件数量"""
        stmt = select(
            Attachment.file_type,
            func.count(Attachment.id).label("count")
        )
        conditions = []
        if user_id is not None:
            conditions.append(Attachment.user_id == user_id)
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.group_by(Attachment.file_type)

        result = db.execute(stmt)
        type_counts = {row.file_type: row.count for row in result.all()}

        # 总数量
        total_stmt = select(func.count(Attachment.id))
        if conditions:
            total_stmt = total_stmt.where(*conditions)
        total = db.execute(total_stmt).scalar() or 0

        return {
            "total": total,
            "type_counts": type_counts
        }

    # ==================== 更新 ====================

    async def update_attachment(
        self, db: AsyncSession, *, attachment_id: int, update_data: dict
    ) -> int:
        """单条更改：支持局部修改"""
        if not update_data:
            return 0
        stmt = update(Attachment).where(Attachment.id == attachment_id).values(**update_data)
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    async def update_by_ids(
        self, db: AsyncSession, *, ids: List[int], update_data: dict
    ) -> int:
        """批量更改"""
        if not update_data:
            return 0
        stmt = update(Attachment).where(Attachment.id.in_(ids)).values(**update_data)
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    # ==================== 删除 ====================

    async def delete(self, db: AsyncSession, *, db_obj: Attachment):
        """单条删除（接收 db_obj）"""
        db.delete(db_obj)
        db.flush()

    async def delete_attachment(self, db: AsyncSession, *, db_obj: Attachment):
        """单条删除（delete 别名，兼容旧调用）"""
        return await self.delete(db, db_obj=db_obj)

    async def delete_by_ids(
        self, db: AsyncSession, *, user_id: int, ids: List[int]
    ) -> int:
        """批量删除（学生端）：带用户归属校验"""
        stmt = delete(Attachment).where(
            Attachment.user_id == user_id,
            Attachment.id.in_(ids)
        )
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    async def delete_by_ids_admin(
        self, db: AsyncSession, *, ids: List[int]
    ) -> int:
        """批量删除（管理端）：无用户归属校验"""
        stmt = delete(Attachment).where(Attachment.id.in_(ids))
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    async def delete_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> int:
        """按用户批量删除（级联清理用户所有附件）"""
        stmt = delete(Attachment).where(Attachment.user_id == user_id)
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    async def delete_by_message(
        self, db: AsyncSession, message_id: int
    ) -> int:
        """按消息ID批量删除（级联清理消息绑定的附件）"""
        stmt = delete(Attachment).where(Attachment.message_id == message_id)
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    # ==================== 导入导出 ====================

    async def export_attachments(
        self, db: AsyncSession, *, user_id: Optional[int] = None
    ) -> List[dict]:
        """数据导出：导出附件列表为字典"""
        stmt = select(Attachment)
        if user_id is not None:
            stmt = stmt.where(Attachment.user_id == user_id)
        stmt = stmt.order_by(desc(Attachment.created_at))
        result = db.execute(stmt)
        attachments = result.scalars().all()

        return [
            {
                "id": a.id,
                "user_id": a.user_id,
                "message_id": a.message_id,
                "file_type": a.file_type,
                "file_url": a.file_url,
                "extracted_text": a.extracted_text,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in attachments
        ]

    async def import_attachments(
        self, db: AsyncSession, *, objs_in: List[dict]
    ) -> int:
        """数据导入：批量导入附件记录"""
        return await self.create_multi(db, objs_in=objs_in)


attachment_crud = CRUDAttachment()