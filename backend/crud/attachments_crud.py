# backend/crud/attachments_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete,update
from typing import List, Optional,Tuple
from models.attachments import Attachment


class CRUDAttachment:

    async def get(self, db: AsyncSession, attachment_id: int) -> Optional[Attachment]:
        """单条查询：获取附件详情"""
        stmt = select(Attachment).where(Attachment.id == attachment_id)
        result = db.execute(stmt)
        return result.scalar_first()

    async def get_multi_attachments(
        self, db: AsyncSession, *, user_id: Optional[int] = None,
        file_type: Optional[str] = None, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Attachment], int]:
        """多条件分页查询：支持按用户、文件类型筛选，返回(列表, 总数)"""
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

    async def create_attachment(
        self, db: AsyncSession, *, user_id: int, file_type: str,
        file_url: str, extracted_text: Optional[str] = None,
        message_id: Optional[int] = None
    ) -> Attachment:
        """带用户归属创建附件记录"""
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

        result = db.execute(stmt)
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
        db.flush()
        return db_obj
    
    async def update_attachment(
        self, db: AsyncSession, *, attachment_id: int, update_data: dict) -> int:
        """单条更新：支持局部修改"""
        if not update_data:
            return 0
        stmt = update(Attachment).where(Attachment.id == attachment_id).values(**update_data)
        result = db.execute(stmt)
        return result.rowcount
    
    async def delete_attachment(db: AsyncSession, *, db_obj: Attachment):
        """物理删除单条附件"""
        db.delete(db_obj)
        db.flush()

attachment_crud = CRUDAttachment()