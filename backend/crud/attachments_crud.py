# backend/crud/attachments_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete
from typing import List, Optional
from models.attachments import Attachment


class CRUDAttachment:

    # 1. 单条查询
    async def get(self, db: AsyncSession, attachment_id: int) -> Optional[Attachment]:
        stmt = select(Attachment).where(Attachment.id == attachment_id)
        result = await db.execute(stmt)
        return result.scalar_first()

    # 2. 分页查询（user_id 为 None 则查全量，用于管理员；传值则查个人，用于学生）
    async def get_multi(
        self, db: AsyncSession, *, user_id: Optional[int] = None,
        file_type: Optional[str] = None, skip: int = 0, limit: int = 20
    ) -> List[Attachment]:
        stmt = select(Attachment)
        if user_id is not None:
            stmt = stmt.where(Attachment.user_id == user_id)
        if file_type:
            stmt = stmt.where(Attachment.file_type.ilike(f"%{file_type}%"))

        stmt = stmt.order_by(desc(Attachment.created_at)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    # 3. 统计符合条件的总记录数（配合分页）
    async def count(
        self, db: AsyncSession, *, user_id: Optional[int] = None,
        file_type: Optional[str] = None
    ) -> int:
        stmt = select(func.count(Attachment.id))
        if user_id is not None:
            stmt = stmt.where(Attachment.user_id == user_id)
        if file_type:
            stmt = stmt.where(Attachment.file_type.ilike(f"%{file_type}%"))

        result = await db.execute(stmt)
        return result.scalar_one()

    # 4. 带用户归属创建
    async def create_with_owner(
        self, db: AsyncSession, *, user_id: int, file_type: str,
        file_url: str, extracted_text: Optional[str] = None,
        message_id: Optional[int] = None
    ) -> Attachment:
        db_obj = Attachment(
            user_id=user_id,
            file_type=file_type,
            file_url=file_url,
            extracted_text=extracted_text,
            message_id=message_id
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    # 5. 物理删除
    async def delete(self, db: AsyncSession, *, db_obj: Attachment):
        await db.delete(db_obj)
        await db.flush()


attachment_crud = CRUDAttachment()