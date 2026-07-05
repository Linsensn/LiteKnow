from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, asc
from sqlalchemy.dialects.mysql import insert
from models.wrong_questions import WrongQuestion
from typing import List, Optional, Dict, Any, Tuple

async def create_wrong_question(db: AsyncSession, *, obj_in: dict, user_id: int) -> WrongQuestion:
    """单条新增"""
    db_obj = WrongQuestion(**obj_in, user_id=user_id)
    db.add(db_obj)
    db.flush()
    return db_obj

async def create_multi_wrong_questions(db: AsyncSession, *, objs_in: List[dict], user_id: int):
    """批量新增"""
    values = [{**obj, "user_id": user_id} for obj in objs_in]
    stmt = insert(WrongQuestion).values(values)
    db.execute(stmt)

async def get_wrong_question(db: AsyncSession, id: int, user_id: int) -> Optional[WrongQuestion]:
    """单条查询"""
    stmt = select(WrongQuestion).where(WrongQuestion.id == id, WrongQuestion.user_id == user_id)
    result = db.execute(stmt)
    return result.scalars().first()

async def get_multi_wrong_questions(
    db: AsyncSession, *, user_id: int, keyword: Optional[str] = None, skip: int = 0, limit: int = 20, sort_by: str = "desc"
) -> Tuple[List[WrongQuestion], int]:
    """分页、模糊搜索及聚合查询，返回 (列表, 总数)"""
    stmt = select(WrongQuestion).where(WrongQuestion.user_id == user_id)
    if keyword:
        stmt = stmt.where(WrongQuestion.question_content.ilike(f"%{keyword}%"))
        
    # 构建并执行统计总数的语句
    count_stmt = select(func.count(WrongQuestion.id)).select_from(WrongQuestion).where(WrongQuestion.user_id == user_id)
    if keyword:
        count_stmt = count_stmt.where(WrongQuestion.question_content.ilike(f"%{keyword}%"))
        
    count_res = db.execute(count_stmt)
    total = count_res.scalar() or 0

    # 构建并执行列表查询的语句
    order_col = desc(WrongQuestion.created_at) if sort_by == "desc" else asc(WrongQuestion.created_at)
    stmt = stmt.order_by(order_col).offset(skip).limit(limit)
    
    result = db.execute(stmt)
    return result.scalars().all(), total

async def update_wrong_question(db: AsyncSession, *, id: int, user_id: int, update_data: Dict[str, Any]):
    """单条更改"""
    if not update_data:
        return
    stmt = update(WrongQuestion).where(WrongQuestion.id == id, WrongQuestion.user_id == user_id).values(**update_data)
    db.execute(stmt)
    
async def update_multi_wrong_questions(db: AsyncSession, *, ids: List[int], user_id: int, update_data: Dict[str, Any]):
    """批量更改"""
    if not update_data:
        return
    stmt = update(WrongQuestion).where(WrongQuestion.id.in_(ids), WrongQuestion.user_id == user_id).values(**update_data)
    db.execute(stmt)

async def delete_wrong_question(db: AsyncSession, *, id: int, user_id: int):
    """单条删除"""
    stmt = delete(WrongQuestion).where(WrongQuestion.id == id, WrongQuestion.user_id == user_id)
    db.execute(stmt)

async def delete_multi_wrong_questions(db: AsyncSession, *, ids: List[int], user_id: int):
    """批量删除"""
    stmt = delete(WrongQuestion).where(WrongQuestion.id.in_(ids), WrongQuestion.user_id == user_id)
    db.execute(stmt)