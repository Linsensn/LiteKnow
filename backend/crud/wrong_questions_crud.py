from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, or_
from models.wrong_questions import WrongQuestion
from typing import List, Optional, Dict, Any

class CRUDWrongQuestion:
    # 1. 新增错题记录
    async def create(self, db: AsyncSession, *, obj_in: dict, user_id: int) -> WrongQuestion:
        db_obj = WrongQuestion(**obj_in, user_id=user_id)
        db.add(db_obj)
        await db.flush()
        return db_obj

    # 2. 分页查询，支持针对题目内容的模糊查询
    async def get_multi(self, db: AsyncSession, *, user_id: int, keyword: Optional[str] = None, skip: int = 0, limit: int = 20):
        stmt = select(WrongQuestion).where(WrongQuestion.user_id == user_id)
        if keyword:
            stmt = stmt.where(WrongQuestion.question_content.ilike(f"%{keyword}%"))
        stmt = stmt.order_by(desc(WrongQuestion.created_at)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count(self, db: AsyncSession, *, user_id: int, keyword: Optional[str] = None):
        stmt = select(func.count(WrongQuestion.id)).where(WrongQuestion.user_id == user_id)
        if keyword:
            stmt = stmt.where(WrongQuestion.question_content.ilike(f"%{keyword}%"))
        result = await db.execute(stmt)
        return result.scalar_one()

    # 3. 单条更改（例如用户补充自己的解析 my_analysis）
    async def update(self, db: AsyncSession, *, id: int, user_id: int, update_data: Dict[str, Any]):
        stmt = update(WrongQuestion).where(WrongQuestion.id == id, WrongQuestion.user_id == user_id).values(**update_data)
        await db.execute(stmt)

    # 4. 单条删除错题
    async def delete(self, db: AsyncSession, *, id: int, user_id: int):
        stmt = delete(WrongQuestion).where(WrongQuestion.id == id, WrongQuestion.user_id == user_id)
        await db.execute(stmt)

wrong_question = CRUDWrongQuestion()