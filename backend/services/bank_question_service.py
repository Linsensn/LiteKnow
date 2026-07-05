# backend/services/bank_question_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from crud.bank_questions_crud import bank_question
from schemas.bank_question_schema import QuestionCreate, QuestionUpdate


class BankQuestionService:

    # 1. 获取单条题目详情
    async def get_question(self, db: AsyncSession, question_id: int):
        question = await bank_question.get(db, question_id=question_id)
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在")
        return question

    # 2. 分页查询题目列表（管理员/学生通用）
    async def get_question_page(
        self, db: AsyncSession, *, bank_id: int = None,
        keyword: str = None, difficulty: str = None,
        page: int, page_size: int
    ):
        skip = (page - 1) * page_size
        total = await bank_question.count(
            db, bank_id=bank_id, keyword=keyword, difficulty=difficulty
        )
        items = await bank_question.get_multi(
            db, bank_id=bank_id, keyword=keyword, difficulty=difficulty,
            skip=skip, limit=page_size
        )
        return {"total": total, "items": items}

    # 3. 单条创建题目
    async def create_question(self, db: AsyncSession, obj_in: QuestionCreate):
        try:
            new_question = await bank_question.create(db, obj_in=obj_in.model_dump())
            await db.commit()
            await db.refresh(new_question)
            return new_question
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"创建失败: {str(e)}")

    # 4. 批量导入题目
    async def create_question_batch(self, db: AsyncSession, objects_in: list[QuestionCreate]):
        try:
            dicts = [obj.model_dump() for obj in objects_in]
            count = await bank_question.create_multi(db, objects_in=dicts)
            await db.commit()
            return count
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"批量导入失败: {str(e)}")

    # 5. 更新题目信息
    async def update_question(self, db: AsyncSession, question_id: int, obj_in: QuestionUpdate):
        # 先校验存在性
        await self.get_question(db, question_id=question_id)
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            await bank_question.update(db, question_id=question_id, update_data=update_data)
            await db.commit()
            return await self.get_question(db, question_id=question_id)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"更新失败: {str(e)}")

    # 6. 逻辑删除题目
    async def delete_question(self, db: AsyncSession, question_id: int):
        await self.get_question(db, question_id=question_id)
        try:
            await bank_question.delete_logical(db, question_id=question_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"删除失败: {str(e)}")


bq_service = BankQuestionService()