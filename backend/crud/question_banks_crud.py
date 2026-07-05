from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, desc
from models.question_banks import QuestionBank
from typing import List, Optional, Dict, Any

class CRUDQuestionBank:
    # 1. 单条新增：接收数据字典和用户ID，创建实体并写入数据库
    async def create(self, db: AsyncSession, *, obj_in: dict, user_id: int) -> QuestionBank:
        db_obj = QuestionBank(**obj_in, user_id=user_id)
        db.add(db_obj)
        await db.flush() # flush 将操作发送到数据库获取自增ID，但不提交事务(commit交由Service层处理)
        return db_obj

    # 2. 批量新增：一次性插入多条数据，提高性能
    async def create_multi(self, db: AsyncSession, *, objs_in: List[dict], user_id: int) -> List[QuestionBank]:
        db_objs = [QuestionBank(**obj, user_id=user_id) for obj in objs_in]
        db.add_all(db_objs)
        await db.flush()
        return db_objs

    # 3. 分页与多条件模糊查询：支持管理员查看所有，学生查看自己的，支持关键词模糊匹配
    async def get_multi(self, db: AsyncSession, *, user_id: Optional[int] = None, keyword: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[QuestionBank]:
        stmt = select(QuestionBank)
        conditions = []
        if user_id is not None:
            conditions.append(QuestionBank.user_id == user_id)
        if keyword:
            # ilike 提供忽略大小写的模糊匹配
            conditions.append(or_(QuestionBank.bank_name.ilike(f"%{keyword}%"), QuestionBank.description.ilike(f"%{keyword}%")))
        if conditions:
            stmt = stmt.where(*conditions)
            
        stmt = stmt.order_by(desc(QuestionBank.created_at)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    # 4. 聚合计算：配合分页功能，获取符合条件的总记录数
    async def count(self, db: AsyncSession, *, user_id: Optional[int] = None, keyword: Optional[str] = None) -> int:
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

    # 5. 单条更改：支持局部更新
    async def update(self, db: AsyncSession, *, bank_id: int, update_data: Dict[str, Any]):
        stmt = update(QuestionBank).where(QuestionBank.id == bank_id).values(**update_data)
        await db.execute(stmt)

    # 6. 批量删除：通过 id 列表进行删除，同时校验 user_id 确保越权安全
    async def delete_multi(self, db: AsyncSession, *, ids: List[int], user_id: Optional[int] = None):
        stmt = delete(QuestionBank).where(QuestionBank.id.in_(ids))
        if user_id is not None:
            stmt = stmt.where(QuestionBank.user_id == user_id)
        await db.execute(stmt)

question_bank = CRUDQuestionBank()