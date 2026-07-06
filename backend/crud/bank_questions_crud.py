# backend/crud/crud_bank_questions.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc,delete
from typing import List, Optional
from models.bank_questions import BankQuestion


class CRUDBankQuestion:

    # 1. 单条查询
    async def get(self, db: AsyncSession, question_id: int) -> Optional[BankQuestion]:
        stmt = select(BankQuestion).where(
            BankQuestion.id == question_id,
        )
        result = db.execute(stmt)
        return result.scalar_first()

    # 2. 分页多条件查询
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 20,
        bank_id: Optional[int] = None, keyword: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[BankQuestion]:
        stmt = select(BankQuestion)
        if bank_id:
            stmt = stmt.where(BankQuestion.bank_id == bank_id)
        if difficulty:
            stmt = stmt.where(BankQuestion.difficulty_level == difficulty)
        if keyword:
            stmt = stmt.where(BankQuestion.content.ilike(f"%{keyword}%"))

        stmt = stmt.order_by(desc(BankQuestion.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    # 3. 统计符合条件的总记录数（配合分页）
    async def count(
        self, db: AsyncSession, *, bank_id: Optional[int] = None,
        keyword: Optional[str] = None, difficulty: Optional[str] = None
    ) -> int:
        stmt = select(func.count(BankQuestion.id))
        if bank_id:
            stmt = stmt.where(BankQuestion.bank_id == bank_id)
        if difficulty:
            stmt = stmt.where(BankQuestion.difficulty_level == difficulty)
        if keyword:
            stmt = stmt.where(BankQuestion.content.ilike(f"%{keyword}%"))

        result = db.execute(stmt)
        return result.scalar_one()

    # 4. 单条新增
    async def create(self, db: AsyncSession, *, obj_in: dict) -> BankQuestion:
        db_obj = BankQuestion(**obj_in)
        db.add(db_obj)
        db.flush()
        return db_obj

    # 5. 批量新增
    async def create_multi(self, db: AsyncSession, *, objects_in: List[dict]) -> int:
        db_objs = [BankQuestion(**obj) for obj in objects_in]
        db.add_all(db_objs)
        db.flush()
        return len(db_objs)

    # 6. 局部更新
    async def update(self, db: AsyncSession, *, question_id: int, update_data: dict):
        stmt = update(BankQuestion).where(
            BankQuestion.id == question_id,
        ).values(**update_data)
        db.execute(stmt)

     # 7. 物理删除
    async def delete(self, db: AsyncSession, *, question_id: int):
        stmt = delete(BankQuestion).where(BankQuestion.id == question_id)
        db.execute(stmt)

bank_question = CRUDBankQuestion()