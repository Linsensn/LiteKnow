from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from crud.crud_question_banks import question_bank

class QuestionBankService:
    async def create_bank(self, db: AsyncSession, current_user: dict, bank_in: dict):
        try:
            new_bank = await question_bank.create(db=db, obj_in=bank_in, user_id=current_user["id"])
            await db.commit()
            return new_bank
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_banks(self, db: AsyncSession, current_user: dict, keyword: str, page: int, page_size: int):
        # 权限逻辑：管理员(admin)传 None 查看全量，学生(student)传自己的 ID
        query_user_id = current_user["id"] if current_user.get("role") != "admin" else None
        skip = (page - 1) * page_size
        
        total = await question_bank.count(db=db, user_id=query_user_id, keyword=keyword)
        items = await question_bank.get_multi(db=db, user_id=query_user_id, keyword=keyword, skip=skip, limit=page_size)
        return {"total": total, "items": items}

    async def bulk_delete(self, db: AsyncSession, current_user: dict, bank_ids: list[int]):
        query_user_id = current_user["id"] if current_user.get("role") != "admin" else None
        try:
            await question_bank.delete_multi(db=db, ids=bank_ids, user_id=query_user_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"删除失败: {str(e)}")

qb_service = QuestionBankService()