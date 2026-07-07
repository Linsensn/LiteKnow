# backend/crud/bank_questions_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc,delete
from typing import List, Optional, Tuple
from models.bank_questions import BankQuestion


class CRUDBankQuestion:

    # 1. 单条查询
    async def get(self, db: AsyncSession, question_id: int) -> Optional[BankQuestion]:
        """单条查询：获取题目详情"""
        stmt = select(BankQuestion).where(
            BankQuestion.id == question_id,
        )
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    # 2. 分页多条件查询（含总数）
    async def get_multi_bank_questions(
        db: AsyncSession, *, skip: int = 0, limit: int = 20,
        bank_id: Optional[int] = None, keyword: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Tuple[List[BankQuestion], int]:
        """多条件分页查询：支持按题库、关键词、难度筛选，返回(列表, 总数)"""
        stmt = select(BankQuestion)
        conditions = []
        if bank_id:
            conditions.append(BankQuestion.bank_id == bank_id)
        if difficulty:
            conditions.append(BankQuestion.difficulty_level == difficulty)
        if keyword:
            conditions.append(BankQuestion.content.ilike(f"%{keyword}%"))

        if conditions:
            stmt = stmt.where(*conditions)

        # 总数查询
        count_stmt = select(func.count(BankQuestion.id)).select_from(BankQuestion)
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        count_res = db.execute(count_stmt)
        total = count_res.scalar() or 0

        stmt = stmt.order_by(desc(BankQuestion.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all(), total

    # 3. 统计符合条件的总记录数
    async def count(
        self, db: AsyncSession, *, bank_id: Optional[int] = None,
        keyword: Optional[str] = None, difficulty: Optional[str] = None
    ) -> int:
        """统计符合条件的题目总数"""
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
        """单条新增题目"""
        db_obj = BankQuestion(**obj_in)
        db.add(db_obj)
        db.flush()
        return db_obj

    # 5. 批量新增
    async def create_multi(self, db: AsyncSession, *, objects_in: List[dict]) -> int:
        """批量新增题目"""
        db_objs = [BankQuestion(**obj) for obj in objects_in]
        db.add_all(db_objs)
        db.flush()
        return len(db_objs)

    # 6. 局部更新
    async def update(self, db: AsyncSession, *, question_id: int, update_data: dict):
        """单条更新：支持局部修改"""
        stmt = update(BankQuestion).where(
            BankQuestion.id == question_id,
        ).values(**update_data)
        db.execute(stmt)

     # 7. 物理删除
    async def delete(self, db: AsyncSession, *, question_id: int):
        """物理删除单条题目"""
        stmt = delete(BankQuestion).where(BankQuestion.id == question_id)
        db.execute(stmt)

    # 按题目 ID 列表批量查询 
    # 用于乱序练习时，前端打乱 ID 顺序后批量拉取题目
    async def get_by_ids(self, db: AsyncSession, *, ids: List[int]) -> List[BankQuestion]:
        """按ID列表批量查询：用于乱序练习时批量拉取题目"""
        stmt = select(BankQuestion).where(BankQuestion.id.in_(ids))
        result = db.execute(stmt)
        return result.scalars().all()
    
    # 统计某个题库的题目数量（按题型分组） — 用于展示题库概览
    async def count_by_bank(self, db: AsyncSession, bank_id: int) -> int:
        """统计某个题库的题目数量"""
        stmt = select(func.count(BankQuestion.id)).where(BankQuestion.bank_id == bank_id)
        result = db.execute(stmt)
        return result.scalar_one()
    
    # 随机获取 N 道题 — 用于乱序练习模式
    async def get_random(self, db: AsyncSession, *, bank_id: int, limit: int = 10) -> List[BankQuestion]:
        """随机获取N道题：用于乱序练习模式"""
        stmt = select(BankQuestion).where(BankQuestion.bank_id == bank_id).order_by(func.rand()).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
bank_question = CRUDBankQuestion()