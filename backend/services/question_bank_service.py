from sqlalchemy.ext.asyncio import AsyncSession
from crud import question_banks_crud
from utils.exceptions import CustomAPIException, ErrorCode
from models.question_banks import QuestionBank

class QuestionBankService:
    async def create_bank(self, db: AsyncSession, current_user: dict, bank_in: dict):
        try:
            new_bank = await question_banks_crud.create_question_bank(db=db, obj_in=bank_in, user_id=current_user["id"])
            await db.commit()
            return new_bank
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(
                code=ErrorCode.QUESTION_BANK_CREATE_FAILED,
                data={"error_detail": str(e)}
            )

    async def get_banks(self, db: AsyncSession, current_user: dict, keyword: str, page: int, page_size: int):
        # 权限逻辑：管理员(admin)传 None 查看全量，学生(student)传自己的 ID
        query_user_id = current_user["id"] if current_user.get("role") != "admin" else None
        skip = (page - 1) * page_size
        
        total = await question_banks_crud.count_question_banks(db=db, user_id=query_user_id, keyword=keyword)
        items = await question_banks_crud.get_multi_question_banks(db=db, user_id=query_user_id, keyword=keyword, skip=skip, limit=page_size)
        return {"total": total, "items": items}

    async def bulk_delete(self, db: AsyncSession, current_user: dict, bank_ids: list[int]):
        query_user_id = current_user["id"] if current_user.get("role") != "admin" else None
        try:
            # 批量操作由 Service 层调用底层的批量语句，并负责 commit
            await question_banks_crud.delete_banks_by_ids(db=db, ids=bank_ids, user_id=query_user_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(
                code=ErrorCode.QUESTION_BANK_DELETE_FAILED,
                data={"error_detail": str(e)}
            )

qb_service = QuestionBankService()