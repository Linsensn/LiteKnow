from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, desc, asc
from sqlalchemy.dialects.mysql import insert
from models.question_banks import QuestionBank
from typing import List, Optional, Dict, Any, Tuple

async def create_question_bank(db: AsyncSession, *, obj_in: dict, user_id: int) -> QuestionBank:
    """单条新增：创建题库并绑定用户"""
    db_obj = QuestionBank(**obj_in, user_id=user_id, total_questions=0)
    db.add(db_obj)
    db.flush() 
    return db_obj

async def create_multi_question_banks(db: AsyncSession, *, objs_in: List[dict], user_id: int):
    """批量新增：供管理员或批量导入时使用"""
    values = [{**obj, "user_id": user_id, "total_questions": 0} for obj in objs_in]
    stmt = insert(QuestionBank).values(values)
    db.execute(stmt)

async def get_question_bank(db: AsyncSession, id: int) -> Optional[QuestionBank]:
    """单条查询：获取详情"""
    stmt = select(QuestionBank).where(QuestionBank.id == id)
    result = db.execute(stmt)
    return result.scalars().first()

async def get_multi_question_banks(
    db: AsyncSession, *, user_id: Optional[int] = None, keyword: Optional[str] = None, 
    skip: int = 0, limit: int = 20, sort_by: str = "desc"
) -> Tuple[List[QuestionBank], int]:
    """多条件模糊分页与聚合查询：返回 (列表, 总数)"""
    stmt = select(QuestionBank)
    conditions = []
    if user_id is not None:
        conditions.append(QuestionBank.user_id == user_id)
    if keyword:
        conditions.append(or_(QuestionBank.bank_name.ilike(f"%{keyword}%"), QuestionBank.description.ilike(f"%{keyword}%")))
    if conditions:
        stmt = stmt.where(*conditions)
        
    count_stmt = select(func.count(QuestionBank.id)).select_from(QuestionBank).where(*conditions) if conditions else select(func.count(QuestionBank.id)).select_from(QuestionBank)
    count_res = db.execute(count_stmt)
    total = count_res.scalar() or 0

    order_col = desc(QuestionBank.created_at) if sort_by == "desc" else asc(QuestionBank.created_at)
    stmt = stmt.order_by(order_col).offset(skip).limit(limit)
    
    result = db.execute(stmt)
    return result.scalars().all(), total

async def update_question_bank(db: AsyncSession, *, bank_id: int, update_data: Dict[str, Any]) -> int:
    """单条更改：支持局部更新"""
    if not update_data:
        return 0
    stmt = update(QuestionBank).where(QuestionBank.id == bank_id).values(**update_data)
    result = db.execute(stmt)
    return result.rowcount

async def update_multi_banks(db: AsyncSession, *, ids: List[int], update_data: Dict[str, Any], user_id: Optional[int] = None) -> int:
    """批量更改：支持权限拦截"""
    if not update_data:
        return 0
    stmt = update(QuestionBank).where(QuestionBank.id.in_(ids))
    if user_id is not None:
        stmt = stmt.where(QuestionBank.user_id == user_id)
    stmt = stmt.values(**update_data)
    result = db.execute(stmt)
    return result.rowcount

async def update_bank_total_questions(db: AsyncSession, *, bank_id: int, increment: int) -> int:
    """原子更新题库下的题目总数（题目增删时调用）"""
    stmt = update(QuestionBank).where(QuestionBank.id == bank_id).values(
        total_questions=QuestionBank.total_questions + increment
    )
    result = db.execute(stmt)
    return result.rowcount

async def delete_banks_by_ids(db: AsyncSession, *, ids: List[int], user_id: Optional[int] = None) -> int:
    """批量/单条物理删除：带权限校验"""
    stmt = delete(QuestionBank).where(QuestionBank.id.in_(ids))
    if user_id is not None:
        stmt = stmt.where(QuestionBank.user_id == user_id)
    result = db.execute(stmt)
    return result.rowcount
