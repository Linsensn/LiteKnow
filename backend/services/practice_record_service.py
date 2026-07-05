import csv
from io import StringIO
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

    async def get_session_analysis(self, db: AsyncSession, session_id: int):
        """获取练习分析报告（调用聚合计算）"""
        return await practice_records_crud.get_session_statistics(db=db, session_id=session_id)

    async def export_user_records_to_csv(self, db: AsyncSession, user_id: int) -> str:
        """
        数据导出：将用户的答题记录导出为 CSV 格式字符串
        """
        records = await practice_records_crud.get_records_with_question_details(
            db=db, user_id=user_id, limit=1000
        )
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["记录ID", "会话ID", "题目类型", "你的答案", "是否正确", "答题时间"])
        
        for r in records:
            q_type = r.question.question_type if hasattr(r, 'question') and r.question else "未知"
            writer.writerow([
                r.id, 
                r.session_id, 
                q_type,
                r.user_answer, 
                "是" if r.is_correct else "否",
                r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
            ])
            
        return output.getvalue()

pr_service = PracticeRecordService()