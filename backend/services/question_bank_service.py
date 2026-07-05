from sqlalchemy.ext.asyncio import AsyncSession
from crud import question_banks_crud
from utils.exceptions import CustomAPIException, ErrorCode

class QuestionBankService:
    async def create_bank(self, db: AsyncSession, current_user: dict, bank_in: dict):
        try:
            new_bank = await question_banks_crud.create_question_bank(db=db, obj_in=bank_in, user_id=current_user["id"])
            await db.commit()
            return new_bank
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.QUESTION_BANK_CREATE_FAILED, data={"error_detail": str(e)})

    async def get_bank_detail(self, db: AsyncSession, current_user: dict, bank_id: int):
        bank = await question_banks_crud.get_question_bank(db=db, id=bank_id)
        if not bank:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND, data={"detail": "题库不存在"})
            
        # 学生端越权校验（Admin可看所有）
        if current_user.get("role") != "admin" and bank.user_id != current_user["id"]:
            raise CustomAPIException(code=ErrorCode.RESOURCE_ACCESS_DENIED, data={"detail": "无权访问此题库"})
        return bank

    async def get_banks(self, db: AsyncSession, current_user: dict, keyword: str, page: int, page_size: int):
        query_user_id = current_user["id"] if current_user.get("role") != "admin" else None
        skip = (page - 1) * page_size
        
        total = await question_banks_crud.count_question_banks(db=db, user_id=query_user_id, keyword=keyword)
        items = await question_banks_crud.get_multi_question_banks(db=db, user_id=query_user_id, keyword=keyword, skip=skip, limit=page_size)
        return {"total": total, "items": items}

    async def update_bank(self, db: AsyncSession, current_user: dict, bank_id: int, update_data: dict):
        # 复用 get_bank_detail 确保题库存在且当前用户有权修改
        await self.get_bank_detail(db=db, current_user=current_user, bank_id=bank_id)
        
        update_dict = {k: v for k, v in update_data.items() if v is not None}
        if not update_dict:
            return
            
        try:
            await question_banks_crud.update_question_bank(db=db, bank_id=bank_id, update_data=update_dict)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.DATABASE_ERROR, data={"detail": str(e)})

    async def bulk_delete(self, db: AsyncSession, current_user: dict, bank_ids: list[int]):
        query_user_id = current_user["id"] if current_user.get("role") != "admin" else None
        try:
            await question_banks_crud.delete_banks_by_ids(db=db, ids=bank_ids, user_id=query_user_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.QUESTION_BANK_DELETE_FAILED, data={"error_detail": str(e)})

qb_service = QuestionBankService()