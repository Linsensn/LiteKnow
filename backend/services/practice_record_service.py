from sqlalchemy.ext.asyncio import AsyncSession
from crud import practice_records_crud, practice_sessions_crud, wrong_questions_crud
from utils.exceptions import CustomAPIException, ErrorCode

class PracticeRecordService:
    async def submit_answer(
        self, db: AsyncSession, user_id: int, session_id: int, question_id: int, 
        user_answer: str, correct_answer: str, question_content: str, current_index: int
    ):
        """
        核心业务编排：记录答案 -> 判定正误 -> 更新进度 -> 错误时自动收录错题本
        """
        is_correct = (user_answer.strip().lower() == correct_answer.strip().lower())
        
        try:
            # 1. Upsert 答题卡记录
            await practice_records_crud.upsert_practice_record(
                db=db, session_id=session_id, user_id=user_id, 
                question_id=question_id, user_answer=user_answer, is_correct=is_correct
            )
            
            # 2. 错题联动收录
            if not is_correct:
                wq_data = {
                    "question_content": question_content,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer
                }
                await wrong_questions_crud.create_wrong_question(db=db, obj_in=wq_data, user_id=user_id)
                
            # 3. 更新练习会话最后的停留位置
            await practice_sessions_crud.update_session_progress(db=db, session_id=session_id, last_viewed_index=current_index)
            
            # 统一提交整个业务的事务
            await db.commit()
            return {"is_correct": is_correct}
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(
                code=ErrorCode.PRACTICE_RECORD_SUBMIT_FAILED,
                data={"error_detail": str(e)}
            )

pr_service = PracticeRecordService()