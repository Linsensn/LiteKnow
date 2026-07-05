from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.dialects.mysql import insert
from models.practice_records import PracticeRecord
from typing import List, Optional, Dict, Any

async def create_practice_record(db: AsyncSession, *, obj_in: dict) -> PracticeRecord:
    """单条新增答题记录：仅将对象添加到 session，不提交事务"""
    db_obj = PracticeRecord(**obj_in)
    db.add(db_obj)
    await db.flush()
    return db_obj

async def upsert_practice_record(db: AsyncSession, *, session_id: int, user_id: int, question_id: int, user_answer: str, is_correct: bool):
    """新增或更新答题记录：利用 MySQL 的 ON DUPLICATE KEY UPDATE 特性，避免同一会话重复插入相同题目"""
    stmt = insert(PracticeRecord).values(
        session_id=session_id,
        user_id=user_id,
        question_id=question_id,
        is_completed=True,
        is_correct=is_correct,
        user_answer=user_answer
    )
    stmt = stmt.on_duplicate_key_update(
        is_completed=True,
        is_correct=is_correct,
        user_answer=user_answer
    )
    await db.execute(stmt)

async def get_practice_record(db: AsyncSession, id: int) -> Optional[PracticeRecord]:
    """单条查询：根据主键 ID 获取答题记录"""
    stmt = select(PracticeRecord).where(PracticeRecord.id == id)
    result = await db.execute(stmt)
    return result.scalar_first()

async def get_records_by_session(db: AsyncSession, *, session_id: int) -> List[PracticeRecord]:
    """会话查询：获取指定练习会话下的所有答题记录，通常用于渲染最终的答题卡"""
    stmt = select(PracticeRecord).where(PracticeRecord.session_id == session_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_multi_records(db: AsyncSession, *, user_id: Optional[int] = None, session_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> List[PracticeRecord]:
    """多条件分页查询：支持按用户、会话进行过滤，按创建时间降序"""
    stmt = select(PracticeRecord)
    conditions = []
    if user_id is not None:
        conditions.append(PracticeRecord.user_id == user_id)
    if session_id is not None:
        conditions.append(PracticeRecord.session_id == session_id)
    
    if conditions:
        stmt = stmt.where(*conditions)
        
    stmt = stmt.order_by(desc(PracticeRecord.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def delete_records_by_ids(db: AsyncSession, *, ids: List[int]):
    """批量条件删除：底层生成 DELETE ... WHERE id IN (...) 语句，由 Service 层控制事务"""
    stmt = delete(PracticeRecord).where(PracticeRecord.id.in_(ids))
    await db.execute(stmt)