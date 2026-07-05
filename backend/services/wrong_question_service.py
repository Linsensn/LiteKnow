from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from crud.wrong_questions_crud import wrong_question

class WrongQuestionService:
    async def get_my_wrong_questions(self, db: AsyncSession, user_id: int, keyword: str, page: int, page_size: int):
        skip = (page - 1) * page_size
        total = await wrong_question.count(db=db, user_id=user_id, keyword=keyword)
        items = await wrong_question.get_multi(db=db, user_id=user_id, keyword=keyword, skip=skip, limit=page_size)
        return {"total": total, "items": items}

    async def update_my_analysis(self, db: AsyncSession, wq_id: int, user_id: int, my_analysis: str):
        try:
            await wrong_question.update(db=db, id=wq_id, user_id=user_id, update_data={"my_analysis": my_analysis})
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def remove_wrong_question(self, db: AsyncSession, wq_id: int, user_id: int):
        try:
            await wrong_question.delete(db=db, id=wq_id, user_id=user_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

wq_service = WrongQuestionService()