from sqlalchemy.ext.asyncio import AsyncSession
from crud import wrong_questions_crud
from utils.exceptions import CustomAPIException, ErrorCode

class WrongQuestionService:
    async def get_my_wrong_questions(self, db: AsyncSession, user_id: int, keyword: str, page: int, page_size: int):
        skip = (page - 1) * page_size
        total = await wrong_questions_crud.count_wrong_questions(db=db, user_id=user_id, keyword=keyword)
        items = await wrong_questions_crud.get_multi_wrong_questions(db=db, user_id=user_id, keyword=keyword, skip=skip, limit=page_size)
        return {"total": total, "items": items}

    async def get_wrong_question_detail(self, db: AsyncSession, wq_id: int, user_id: int):
        """获取错题详情，已在 CRUD 层限制 user_id"""
        wq = await wrong_questions_crud.get_wrong_question(db=db, id=wq_id, user_id=user_id)
        if not wq:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND, data={"detail": "错题不存在或无权访问"})
        return wq

    async def update_my_analysis(self, db: AsyncSession, wq_id: int, user_id: int, my_analysis: str):
        try:
            await wrong_questions_crud.update_wrong_question(db=db, id=wq_id, user_id=user_id, update_data={"my_analysis": my_analysis})
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.WRONG_QUESTION_UPDATE_FAILED, data={"error_detail": str(e)})

    async def remove_wrong_question(self, db: AsyncSession, wq_id: int, user_id: int):
        try:
            await wrong_questions_crud.delete_wrong_question(db=db, id=wq_id, user_id=user_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.WRONG_QUESTION_DELETE_FAILED, data={"error_detail": str(e)})

    async def bulk_remove_wrong_questions(self, db: AsyncSession, wq_ids: list[int], user_id: int):
        try:
            await wrong_questions_crud.delete_multi_wrong_questions(db=db, ids=wq_ids, user_id=user_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.DATABASE_ERROR, data={"detail": str(e)})

    async def bulk_import_wrong_questions(self, db: AsyncSession, user_id: int, questions_data: list[dict]):
        """从外部批量导入错题"""
        try:
            await wrong_questions_crud.create_multi_wrong_questions(db=db, objs_in=questions_data, user_id=user_id)
            await db.commit()
            return len(questions_data)
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.WRONG_QUESTION_CREATE_FAILED, data={"error_detail": str(e)})

wq_service = WrongQuestionService()