from sqlalchemy.ext.asyncio import AsyncSession
from crud import wrong_questions_crud
from utils.exceptions import CustomAPIException, ErrorCode
from models.wrong_questions import WrongQuestion

class WrongQuestionService:
    async def get_my_wrong_questions(self, db: AsyncSession, user_id: int, keyword: str, page: int, page_size: int):
        skip = (page - 1) * page_size
        total = await wrong_questions_crud.count_wrong_questions(db=db, user_id=user_id, keyword=keyword)
        items = await wrong_questions_crud.get_multi_wrong_questions(db=db, user_id=user_id, keyword=keyword, skip=skip, limit=page_size)
        return {"total": total, "items": items}

    async def update_my_analysis(self, db: AsyncSession, wq_id: int, user_id: int, my_analysis: str):
        try:
            await wrong_questions_crud.update_wrong_question(db=db, id=wq_id, user_id=user_id, update_data={"my_analysis": my_analysis})
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(
                code=ErrorCode.WRONG_QUESTION_UPDATE_FAILED,
                data={"error_detail": str(e)}
            )

    async def remove_wrong_question(self, db: AsyncSession, wq_id: int, user_id: int):
        try:
            await wrong_questions_crud.delete_wrong_question(db=db, id=wq_id, user_id=user_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(
                code=ErrorCode.WRONG_QUESTION_DELETE_FAILED,
                data={"error_detail": str(e)}
            )

    # 业务层接管批量新增能力（例如从外部数据批量导入错题）
    async def bulk_import_wrong_questions(self, db: AsyncSession, user_id: int, questions_data: list[dict]):
        try:
            # 业务层直接利用原生的 SQLAlchemy add_all 进行批量写入事务管理
            db_objs = [WrongQuestion(**obj, user_id=user_id) for obj in questions_data]
            db.add_all(db_objs)
            await db.commit()
            return len(db_objs)
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(
                code=ErrorCode.WRONG_QUESTION_CREATE_FAILED,
                data={"error_detail": str(e)}
            )

wq_service = WrongQuestionService()