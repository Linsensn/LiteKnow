from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc, asc, func, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.mysql import insert
from models.practice_sessions import PracticeSession
from typing import List, Optional, Tuple

async def create_practice_session(db: AsyncSession, *, obj_in: dict) -> PracticeSession:
    """单条新增"""
    db_obj = PracticeSession(**obj_in)
    db.add(db_obj)
    await db.flush()
    return db_obj

async def create_multi_sessions(db: AsyncSession, *, objs_in: List[dict]):
    """批量新增"""
    stmt = insert(PracticeSession).values(objs_in)
    await db.execute(stmt)

async def get_practice_session(db: AsyncSession, id: int) -> Optional[PracticeSession]:
    """单条查询"""
    stmt = select(PracticeSession).where(PracticeSession.id == id)
    result = await db.execute(stmt)
    return result.scalar_first()

async def get_multi_sessions(
    db: AsyncSession, *, user_id: Optional[int] = None, status: Optional[str] = None, 
    search_keyword: Optional[str] = None, skip: int = 0, limit: int = 20, sort_by: str = "desc"
) -> Tuple[List[PracticeSession], int]:
    """分页、多条件、模糊搜索(针对模式)、关联查询(题库)与聚合总数"""
    stmt = select(PracticeSession).options(joinedload(PracticeSession.bank))
    conditions = []
    
    if user_id is not None:
        conditions.append(PracticeSession.user_id == user_id)
    if status is not None:
        conditions.append(PracticeSession.status == status)
    if search_keyword:
        conditions.append(PracticeSession.practice_mode.like(f"%{search_keyword}%"))
        
    if conditions:
        stmt = stmt.where(*conditions)
        
    # 🌟 修复：采用最稳妥的 execute + scalar 写法
    count_stmt = select(func.count(PracticeSession.id)).select_from(PracticeSession).where(*conditions) if conditions else select(func.count(PracticeSession.id)).select_from(PracticeSession)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0
    
    # 排序与分页
    order_col = desc(PracticeSession.created_at) if sort_by == "desc" else asc(PracticeSession.created_at)
    stmt = stmt.order_by(order_col).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all(), total

async def update_session(db: AsyncSession, *, id: int, obj_in: dict):
    """单条更改"""
    stmt = update(PracticeSession).where(PracticeSession.id == id).values(**obj_in)
    await db.execute(stmt)

async def update_multi_sessions(db: AsyncSession, *, ids: List[int], obj_in: dict):
    """批量更改"""
    stmt = update(PracticeSession).where(PracticeSession.id.in_(ids)).values(**obj_in)
    await db.execute(stmt)

async def update_session_progress(db: AsyncSession, *, session_id: int, last_viewed_index: int, status: str = None):
    """局部状态/进度更新"""
    values = {"last_viewed_index": last_viewed_index}
    if status:
        values["status"] = status
    stmt = update(PracticeSession).where(PracticeSession.id == session_id).values(**values)
    await db.execute(stmt)

async def delete_sessions_by_ids(db: AsyncSession, *, ids: List[int]):
    """单条/批量物理删除"""
    stmt = delete(PracticeSession).where(PracticeSession.id.in_(ids))
    await db.execute(stmt)