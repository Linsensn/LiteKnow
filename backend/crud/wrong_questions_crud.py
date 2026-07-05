from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, or_
from models.wrong_questions import WrongQuestion
from typing import List, Optional, Dict, Any

async def create_wrong_question(db: AsyncSession, *, obj_in: dict, user_id: int) -> WrongQuestion:
    """单条新增：通常由 Service 层在答错题时自动调用"""
    db_obj = WrongQuestion(**obj_in, user_id=user_id)
    db.add(db_obj)
    await db.flush()
    return db_obj

async def get_wrong_question(db: AsyncSession, id: int) -> Optional[WrongQuestion]:
    """单条查询：获取具体的错题记录详情"""
    stmt = select(WrongQuestion).where(WrongQuestion.id == id)
    result = await db.execute(stmt)
    return result.scalar_first()

async def get_multi_wrong_questions(db: AsyncSession, *, user_id: int, keyword: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[WrongQuestion]:
    """分页与模糊查询：用户个人错题本，支持对题干内容(question_content)进行模糊搜索"""
    stmt = select(WrongQuestion).where(WrongQuestion.user_id == user_id)
    if keyword:
        stmt = stmt.where(WrongQuestion.question_content.ilike(f"%{keyword}%"))
    stmt = stmt.order_by(desc(WrongQuestion.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def count_wrong_questions(db: AsyncSession, *, user_id: int, keyword: Optional[str] = None) -> int:
    """聚合查询：统计个人的错题总数"""
    stmt = select(func.count(WrongQuestion.id)).where(WrongQuestion.user_id == user_id)
    if keyword:
        stmt = stmt.where(WrongQuestion.question_content.ilike(f"%{keyword}%"))
    result = await db.execute(stmt)
    return result.scalar_one()

async def update_wrong_question(db: AsyncSession, *, id: int, user_id: int, update_data: Dict[str, Any]):
    """单条更改：限定 user_id 以保证只能修改自己的记录（如：添加 my_analysis）"""
    stmt = update(WrongQuestion).where(WrongQuestion.id == id, WrongQuestion.user_id == user_id).values(**update_data)
    await db.execute(stmt)

async def delete_wrong_question(db: AsyncSession, *, id: int, user_id: int):
    """单条删除：掌握错题后将其从错题本中移除"""
    stmt = delete(WrongQuestion).where(WrongQuestion.id == id, WrongQuestion.user_id == user_id)
    await db.execute(stmt)