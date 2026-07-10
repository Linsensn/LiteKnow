# backend/services/bank_question_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from utils.exceptions import CustomAPIException, ErrorCode
from crud.bank_questions_crud import bank_question
from crud.question_banks_crud import update_bank_total_questions
from crud.favorites_crud import favorite_crud
from schemas.bank_question_schema import QuestionCreate, QuestionUpdate
from schemas.common import PageResult

class BankQuestionService:

    # 1. 获取单条题目详情
    async def get_question(self, db: AsyncSession, question_id: int):
        question = await bank_question.get(db, question_id=question_id)
        if not question:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND)
        return question

    # 2. 分页查询题目列表（管理员/学生通用）
    async def get_question_page(
        self, db: AsyncSession, *, bank_id: int = None,
        keyword: str = None, difficulty: str = None,
        page: int, page_size: int
    ):
        skip = (page - 1) * page_size
        items, total = await bank_question.get_multi(         # ← 元组解包，count 已内含
            db, bank_id=bank_id, keyword=keyword, difficulty=difficulty,
            skip=skip, limit=page_size
        )
        return PageResult(
            list=items,
            total=total,
            page=page,
            page_size=page_size
        )

    # 3. 单条创建题目
    async def create_question(self, db: AsyncSession, obj_in: QuestionCreate):
        try:
            new_question = await bank_question.create(db, obj_in=obj_in.model_dump())
            # 同步更新父题库的 total_questions +1
            if new_question.bank_id:
                await update_bank_total_questions(db, bank_id=new_question.bank_id, increment=1)
            db.commit()
            db.refresh(new_question)
            return new_question
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.QUESTION_BANK_CREATE_FAILED)


    # 4. 批量导入题目
    async def create_question_batch(self, db: AsyncSession, objects_in: list[QuestionCreate]):
        try:
            dicts = [obj.model_dump() for obj in objects_in]
            count = await bank_question.create_multi(db, objects_in=dicts)
            # 同步更新父题库的 total_questions +count（所有题目属于同一个 bank_id）
            if dicts and dicts[0].get("bank_id"):
                await update_bank_total_questions(db, bank_id=dicts[0]["bank_id"], increment=count)
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.QUESTION_BANK_CREATE_FAILED)

    # 5. 更新题目信息
    async def update_question(self, db: AsyncSession, question_id: int, obj_in: QuestionUpdate):
        # 先校验存在性
        await self.get_question(db, question_id=question_id)
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            await bank_question.update(db, question_id=question_id, update_data=update_data)
            db.commit()
            return await self.get_question(db, question_id=question_id)
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # 6. 删除题目
    async def delete_question(self, db: AsyncSession, question_id: int):
        question = await self.get_question(db, question_id=question_id)
        bank_id = question.bank_id
        try:
            # 级联清理收藏夹中对应的题目ID
            await favorite_crud.remove_content_ids_by_type(
                db, content_type="question", content_ids=[question_id]
            )
            await bank_question.delete(db, question_id=question_id)
            # 同步更新父题库的 total_questions -1
            if bank_id:
                await update_bank_total_questions(db, bank_id=bank_id, increment=-1)
            db.commit()
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.QUESTION_BANK_DELETE_FAILED)


bq_service = BankQuestionService()