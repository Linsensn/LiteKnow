import csv
from io import StringIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from crud import wrong_questions_crud
from utils.exceptions import CustomAPIException, ErrorCode

class WrongQuestionService:
    async def get_my_wrong_questions(self, db: AsyncSession, user_id: int, keyword: str, page: int, page_size: int, sort_by: str = "desc"):
        skip = (page - 1) * page_size
        items, total = await wrong_questions_crud.get_multi_wrong_questions(
            db=db, user_id=user_id, keyword=keyword, skip=skip, limit=page_size, sort_by=sort_by
        )
        return {"total": total, "items": items}

    async def get_wrong_question_detail(self, db: AsyncSession, wq_id: int, user_id: int):
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
        try:
            await wrong_questions_crud.create_multi_wrong_questions(db=db, objs_in=questions_data, user_id=user_id)
            await db.commit()
            return len(questions_data)
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.WRONG_QUESTION_CREATE_FAILED, data={"error_detail": str(e)})

    async def export_wrong_questions_to_csv(self, db: AsyncSession, user_id: int) -> str:
        """业务层：导出数据 (CSV)"""
        items, _ = await wrong_questions_crud.get_multi_wrong_questions(db=db, user_id=user_id, limit=2000)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["错题ID", "题目内容", "你的答案", "正确答案", "个人解析", "收录时间"])
        for w in items:
            writer.writerow([
                w.id, w.question_content, w.user_answer or "", w.correct_answer or "", 
                w.my_analysis or "", w.created_at.strftime("%Y-%m-%d %H:%M:%S") if w.created_at else ""
            ])
        return output.getvalue()
        
    async def import_wrong_questions_from_csv(self, db: AsyncSession, user_id: int, file: UploadFile):
        """业务层：从文件导入错题"""
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(StringIO(decoded))
        objs_in = []
        for row in reader:
            objs_in.append({
                "question_content": row.get("题目内容", ""),
                "user_answer": row.get("你的答案", ""),
                "correct_answer": row.get("正确答案", ""),
                "my_analysis": row.get("个人解析", "")
            })
        if objs_in:
            await self.bulk_import_wrong_questions(db=db, user_id=user_id, questions_data=objs_in)

wq_service = WrongQuestionService()