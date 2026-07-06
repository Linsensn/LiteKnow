import csv
import json
from io import StringIO
from typing import Any, List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from crud import practice_records_crud, practice_sessions_crud, wrong_questions_crud
from utils.exceptions import CustomAPIException, ErrorCode

class PracticeRecordService:
    async def submit_answer(
        self, db: AsyncSession, user_id: int, session_id: int, question_id: int, 
        user_answer: Any, correct_answer: Any, question_content: str, current_index: int,
        option_sequence: Optional[List[str]] = None
    ):
        """核心业务编排：提交单题作答"""
        
        # 1. 判断逻辑升级：支持 JSON (列表/字典) 的比对
        if isinstance(user_answer, list) and isinstance(correct_answer, list):
            # 对于数组形式(单选/多选)，排序后比对，避免选项顺序影响判断
            is_correct = sorted(user_answer) == sorted(correct_answer)
        elif isinstance(user_answer, str) and isinstance(correct_answer, str):
            # 兼容旧版的纯字符串比较
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        else:
            # 其他 JSON 结构(如字典)直接做全等比对
            is_correct = user_answer == correct_answer

        try:
            # 2. 传递 option_sequence 并保存记录
            await practice_records_crud.upsert_practice_record(
                db=db, session_id=session_id, user_id=user_id, 
                question_id=question_id, user_answer=user_answer, is_correct=is_correct,
                option_sequence=option_sequence
            )
            
            if not is_correct:
                # 3. 错题本兼容：wrong_questions表的答案字段为varchar，需要将JSON转为字符串
                wq_user_ans_str = json.dumps(user_answer, ensure_ascii=False) if not isinstance(user_answer, str) else user_answer
                wq_corr_ans_str = json.dumps(correct_answer, ensure_ascii=False) if not isinstance(correct_answer, str) else correct_answer
                
                wq_data = {
                    "question_content": question_content, 
                    "user_answer": wq_user_ans_str, 
                    "correct_answer": wq_corr_ans_str
                }
                await wrong_questions_crud.create_wrong_question(db=db, obj_in=wq_data, user_id=user_id)
                
            await practice_sessions_crud.update_session_progress(db=db, session_id=session_id, last_viewed_index=current_index)
            db.commit()
            return {"is_correct": is_correct}
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.PRACTICE_RECORD_SUBMIT_FAILED, data={"error_detail": str(e)})

    async def get_session_analysis(self, db: AsyncSession, session_id: int):
        """获取练习分析报告"""
        return await practice_records_crud.get_session_statistics(db=db, session_id=session_id)

    async def export_user_records_to_csv(self, db: AsyncSession, user_id: int) -> str:
        """数据导出"""
        records = await practice_records_crud.get_records_with_question_details(db=db, user_id=user_id, limit=1000)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["记录ID", "会话ID", "题目类型", "你的答案", "是否正确", "答题时间"])
        for r in records:
            q_type = r.question.question_type if hasattr(r, 'question') and r.question else "未知"
            # 将 JSON 答案序列化为字符串进行导出
            user_answer_str = json.dumps(r.user_answer, ensure_ascii=False) if r.user_answer is not None else ""
            
            writer.writerow([
                r.id, r.session_id, q_type, user_answer_str, 
                "是" if r.is_correct else "否", 
                r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
            ])
        return output.getvalue()
        
    async def import_user_records_from_csv(self, db: AsyncSession, user_id: int, file: UploadFile):
        """数据导入（简易实现）"""
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(StringIO(decoded))
        objs_in = []
        for row in reader:
            raw_answer = row.get("你的答案", "")
            # 尝试将导入的答案字符串反序列化回 JSON 对象
            try:
                parsed_answer = json.loads(raw_answer) if raw_answer else None
            except json.JSONDecodeError:
                parsed_answer = raw_answer

            objs_in.append({
                "user_id": user_id,
                "session_id": int(row.get("会话ID", 0)),
                "question_id": int(row.get("题目ID", 0)),
                "user_answer": parsed_answer,
                "is_correct": True if row.get("是否正确") == "是" else False,
                "is_completed": True
            })
        if objs_in:
            await practice_records_crud.create_multi_records(db=db, objs_in=objs_in)
            db.commit()

pr_service = PracticeRecordService()