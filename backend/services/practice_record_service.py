from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from crud.crud_practice_records import practice_record
from crud.crud_practice_sessions import practice_session
from crud.crud_wrong_questions import wrong_question

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
            await practice_record.upsert(
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
                await wrong_question.create(db=db, obj_in=wq_data, user_id=user_id)
                
            # 3. 更新练习会话最后的停留位置
            await practice_session.update_progress(db=db, session_id=session_id, last_viewed_index=current_index)
            
            await db.commit()
            return {"is_correct": is_correct}
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

pr_service = PracticeRecordService()