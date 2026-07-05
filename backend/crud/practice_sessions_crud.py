from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc, func
from models.practice_sessions import PracticeSession
from typing import List, Optional, Dict, Any

async def create_practice_session(db: AsyncSession, *, user_id: int, bank_id: int, practice_mode: str, question_sequence: list) -> PracticeSession:
    """创建练习会话：初始化 JSON 格式的题目序列和起始状态"""
    db_obj = PracticeSession(
        user_id=user_id,
        bank_id=bank_id,
        practice_mode=practice_mode,
        question_sequence=question_sequence,
        last_viewed_index=0,
        status="ongoing"
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def get_practice_session(db: AsyncSession, id: int) -> Optional[PracticeSession]:
    """单条查询：获取会话详情，常用于恢复练习进度"""
    stmt = select(PracticeSession).where(PracticeSession.id == id)
    result = await db.execute(stmt)
    return result.scalar_first()

async def get_multi_sessions(db: AsyncSession, *, user_id: Optional[int] = None, status: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[PracticeSession]:
    """分页查询：查询历史会话列表，支持通过状态（如 ongoing, completed）过滤"""
    stmt = select(PracticeSession)
    conditions = []
    if user_id is not None:
        conditions.append(PracticeSession.user_id == user_id)
    if status is not None:
        conditions.append(PracticeSession.status == status)
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.order_by(desc(PracticeSession.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def count_sessions(db: AsyncSession, *, user_id: Optional[int] = None, status: Optional[str] = None) -> int:
    """聚合查询：统计符合条件的练习会话总数，用于分页计算"""
    stmt = select(func.count(PracticeSession.id))
    conditions = []
    if user_id is not None:
        conditions.append(PracticeSession.user_id == user_id)
    if status is not None:
        conditions.append(PracticeSession.status == status)
    if conditions:
        stmt = stmt.where(*conditions)
    result = await db.execute(stmt)
    return result.scalar_one()

async def update_session_progress(db: AsyncSession, *, session_id: int, last_viewed_index: int, status: str = None):
    """状态更新：局部更新会话的查看进度或交卷状态"""
    values = {"last_viewed_index": last_viewed_index}
    if status:
        values["status"] = status
    stmt = update(PracticeSession).where(PracticeSession.id == session_id).values(**values)
    await db.execute(stmt)

async def delete_sessions_by_ids(db: AsyncSession, *, ids: List[int]):
    """批量条件删除：通过 ID 列表进行原生批量删除"""
    stmt = delete(PracticeSession).where(PracticeSession.id.in_(ids))
    await db.execute(stmt)