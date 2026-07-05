from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, asc, case
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.mysql import insert
from models.practice_records import PracticeRecord
from typing import List, Optional, Tuple

async def create_practice_record(db: AsyncSession, *, obj_in: dict) -> PracticeRecord:
    """单条新增"""
    db_obj = PracticeRecord(**obj_in)
    db.add(db_obj)
    db.flush()
    return db_obj

async def create_multi_records(db: AsyncSession, *, objs_in: List[dict]):
    """批量新增"""
    stmt = insert(PracticeRecord).values(objs_in)
    db.execute(stmt)

async def upsert_practice_record(db: AsyncSession, *, session_id: int, user_id: int, question_id: int, user_answer: str, is_correct: bool):
    """新增或更新：处理唯一键冲突"""
    stmt = insert(PracticeRecord).values(
        session_id=session_id, user_id=user_id, question_id=question_id,
        is_completed=True, is_correct=is_correct, user_answer=user_answer
    )
    stmt = stmt.on_duplicate_key_update(
        is_completed=True, is_correct=is_correct, user_answer=user_answer
    )
    db.execute(stmt)

async def update_record(db: AsyncSession, *, id: int, obj_in: dict) -> None:
    """单条更改"""
    stmt = update(PracticeRecord).where(PracticeRecord.id == id).values(**obj_in)
    db.execute(stmt)

async def update_multi_records(db: AsyncSession, *, ids: List[int], obj_in: dict) -> None:
    """批量更改"""
    stmt = update(PracticeRecord).where(PracticeRecord.id.in_(ids)).values(**obj_in)
    db.execute(stmt)

async def toggle_record_status(db: AsyncSession, *, id: int, is_correct: bool) -> None:
    """状态切换"""
    stmt = update(PracticeRecord).where(PracticeRecord.id == id).values(is_correct=is_correct)
    db.execute(stmt)

async def get_practice_record(db: AsyncSession, id: int) -> Optional[PracticeRecord]:
    """单条查询"""
    stmt = select(PracticeRecord).where(PracticeRecord.id == id)
    result = db.execute(stmt)
    return result.scalars().first()

async def get_multi_records(
    db: AsyncSession, *, user_id: Optional[int] = None, session_id: Optional[int] = None, 
    is_correct: Optional[bool] = None, skip: int = 0, limit: int = 20, sort_by: str = "desc"
) -> Tuple[List[PracticeRecord], int]:
    """多条件分页与排序查询，返回列表和总数"""
    stmt = select(PracticeRecord)
    conditions = []
    if user_id is not None:
        conditions.append(PracticeRecord.user_id == user_id)
    if session_id is not None:
        conditions.append(PracticeRecord.session_id == session_id)
    if is_correct is not None:
        conditions.append(PracticeRecord.is_correct == is_correct)
    
    if conditions:
        stmt = stmt.where(*conditions)
        
    count_stmt = select(func.count(PracticeRecord.id)).select_from(PracticeRecord).where(*conditions) if conditions else select(func.count(PracticeRecord.id)).select_from(PracticeRecord)
    count_res = db.execute(count_stmt)
    total = count_res.scalar() or 0
        
    order_col = desc(PracticeRecord.created_at) if sort_by == "desc" else asc(PracticeRecord.created_at)
    stmt = stmt.order_by(order_col).offset(skip).limit(limit)
    result = db.execute(stmt)
    
    return result.scalars().all(), total

async def get_records_with_question_details(db: AsyncSession, *, user_id: int, user_answer_keyword: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[PracticeRecord]:
    """模糊与关联查询"""
    # 移除了无效的 .options(joinedload(PracticeRecord.question))
    stmt = select(PracticeRecord).where(PracticeRecord.user_id == user_id)
    if user_answer_keyword:
        stmt = stmt.where(PracticeRecord.user_answer.like(f"%{user_answer_keyword}%"))
    stmt = stmt.order_by(desc(PracticeRecord.created_at)).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()

async def get_session_statistics(db: AsyncSession, *, session_id: int) -> dict:
    """聚合计算"""
    stmt = select(
        func.count(PracticeRecord.id).label("total_questions"),
        func.sum(case((PracticeRecord.is_completed == True, 1), else_=0)).label("completed_count"),
        func.sum(case((PracticeRecord.is_correct == True, 1), else_=0)).label("correct_count")
    ).where(PracticeRecord.session_id == session_id)
    
    result = db.execute(stmt)
    row = result.first()
    total = row.total_questions or 0
    correct = row.correct_count or 0
    return {
        "total": total,
        "completed": row.completed_count or 0,
        "correct": correct,
        "accuracy_rate": round(correct / total, 4) if total > 0 else 0.0
    }

async def delete_records_by_ids(db: AsyncSession, *, ids: List[int]):
    """单条/批量物理删除"""
    stmt = delete(PracticeRecord).where(PracticeRecord.id.in_(ids))
    db.execute(stmt)