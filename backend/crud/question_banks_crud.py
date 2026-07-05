from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, desc
from models.question_banks import QuestionBank
from typing import List, Optional, Dict, Any

async def create_question_bank(db: AsyncSession, *, obj_in: dict, user_id: int) -> QuestionBank:
    """单条新增：根据传入的数据字典创建题库，并绑定用户"""
    db_obj = QuestionBank(**obj_in, user_id=user_id)
    db.add(db_obj)
    await db.flush() 
    return db_obj

async def get_question_bank(db: AsyncSession, id: int) -> Optional[QuestionBank]:
    """单条查询：根据题库 ID 获取详情"""
    stmt = select(QuestionBank).where(QuestionBank.id == id)
    result = await db.execute(stmt)
    return result.scalar_first()

async def get_multi_question_banks(db: AsyncSession, *, user_id: Optional[int] = None, keyword: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[QuestionBank]:
    """多条件模糊分页查询：支持按题库名或描述进行关键字匹配"""
    stmt = select(QuestionBank)
    conditions = []
    if user_id is not None:
        conditions.append(QuestionBank.user_id == user_id)
    if keyword:
        conditions.append(or_(QuestionBank.bank_name.ilike(f"%{keyword}%"), QuestionBank.description.ilike(f"%{keyword}%")))
    if conditions:
        stmt = stmt.where(*conditions)
        
    stmt = stmt.order_by(desc(QuestionBank.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def count_question_banks(db: AsyncSession, *, user_id: Optional[int] = None, keyword: Optional[str] = None) -> int:
    """聚合查询：统计符合模糊查询条件的题库总数"""
    stmt = select(func.count(QuestionBank.id))
    conditions = []
    if user_id is not None:
        conditions.append(QuestionBank.user_id == user_id)
    if keyword:
        conditions.append(or_(QuestionBank.bank_name.ilike(f"%{keyword}%"), QuestionBank.description.ilike(f"%{keyword}%")))
    if conditions:
        stmt = stmt.where(*conditions)
    result = await db.execute(stmt)
    return result.scalar_one()

async def update_question_bank(db: AsyncSession, *, bank_id: int, update_data: Dict[str, Any]):
    """单条更改：支持传入字典对题库信息进行局部更新"""
    stmt = update(QuestionBank).where(QuestionBank.id == bank_id).values(**update_data)
    await db.execute(stmt)

async def delete_banks_by_ids(db: AsyncSession, *, ids: List[int], user_id: Optional[int] = None):
    """批量条件删除：带权限校验，如果是学生仅能删除 user_id 匹配的数据"""
    stmt = delete(QuestionBank).where(QuestionBank.id.in_(ids))
    if user_id is not None:
        stmt = stmt.where(QuestionBank.user_id == user_id)
    await db.execute(stmt)