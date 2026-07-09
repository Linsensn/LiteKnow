import csv
import random
from io import StringIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from crud import practice_sessions_crud
from models.bank_questions import BankQuestion
from models.wrong_questions import WrongQuestion
from models.practice_records import PracticeRecord  # 🌟 新增导入：引入练习记录模型
from utils.exceptions import CustomAPIException, ErrorCode

class PracticeSessionService:
    async def start_new_session(self, db: AsyncSession, user_id: int, bank_id: int, mode: str, is_options_shuffled: bool, question_sequence: list):
        """核心业务：创建会话（根据模式混淆题目顺序）"""
        sequence = question_sequence.copy() if question_sequence else []
        
        if not sequence:
            if mode == "mistake":
                stmt = select(WrongQuestion.question_id).join(
                    BankQuestion, WrongQuestion.question_id == BankQuestion.id
                ).where(
                    WrongQuestion.user_id == user_id,
                    BankQuestion.bank_id == bank_id
                )
            else:
                stmt = select(BankQuestion.id).where(BankQuestion.bank_id == bank_id)

            result = db.execute(stmt)
            sequence = list(result.scalars().all())
            
        if not sequence:
            if mode == "mistake":
                raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND, data={"detail": "太棒了，你在这个题库里还没有错题！"})
            else:
                raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND, data={"detail": "该题库下暂时没有题目哦"})

        if mode == "random" or mode == "mistake":
            random.shuffle(sequence)
            
        try:
            obj_in = {
                "user_id": user_id, 
                "bank_id": bank_id, 
                "practice_mode": mode, 
                "is_options_shuffled": is_options_shuffled,
                "question_sequence": sequence,
                "last_viewed_index": 0, 
                "status": "ongoing"
            }
            new_session = await practice_sessions_crud.create_practice_session(db=db, obj_in=obj_in)
            db.commit()
            return new_session
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.PRACTICE_SESSION_CREATE_FAILED, data={"error_detail": str(e)})

    async def get_session_detail(self, db: AsyncSession, session_id: int, user_id: int):
        """查询详情并鉴权"""
        session = await practice_sessions_crud.get_practice_session(db=db, id=session_id)
        if not session or session.user_id != user_id:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND, data={"detail": "会话不存在或无权访问"})
        return session

    async def submit_session(self, db: AsyncSession, session_id: int, user_id: int):
        """主动交卷"""
        await self.get_session_detail(db=db, session_id=session_id, user_id=user_id) 
        try:
            await practice_sessions_crud.update_session_progress(db=db, session_id=session_id, last_viewed_index=0, status="completed")
            db.commit()
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DATABASE_ERROR, data={"detail": str(e)})

    async def export_sessions_to_csv(self, db: AsyncSession, user_id: int) -> str:
        """业务层：数据导出"""
        sessions, _ = await practice_sessions_crud.get_multi_sessions(db=db, user_id=user_id, limit=1000)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["会话ID", "题库名称", "练习模式", "选项乱序", "状态", "创建时间"])
        for s in sessions:
            b_name = s.bank.bank_name if hasattr(s, 'bank') and s.bank else "未知题库"
            writer.writerow([s.id, b_name, s.practice_mode, "是" if s.is_options_shuffled else "否", s.status, s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else ""])
        return output.getvalue()
        
    async def import_sessions_from_csv(self, db: AsyncSession, user_id: int, file: UploadFile):
        """业务层：数据导入"""
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(StringIO(decoded))
        objs_in = []
        for row in reader:
            objs_in.append({
                "user_id": user_id,
                "bank_id": int(row.get("题库ID", 0)),
                "practice_mode": row.get("练习模式", "sequential"),
                "is_options_shuffled": row.get("选项乱序", "否") == "是",
                "status": row.get("状态", "ongoing"),
                "question_sequence": [],
                "last_viewed_index": 0
            })
        if objs_in:
            await practice_sessions_crud.create_multi_sessions(db=db, objs_in=objs_in)
            db.commit()

    async def grade_and_submit_session(self, db: AsyncSession, session_id: int, user_id: int, user_answers_map: dict):
        """核心业务：交卷判题，并自动收录错题"""
        # 1. 查出会话信息
        session = await self.get_session_detail(db, session_id, user_id)
        sequence = session.question_sequence

        if not sequence:
            session.status = "completed"
            db.commit()
            return {"total": 0, "wrong_count": 0}

        # 2. 一次性查出这份卷子所有的题目详情（为了获取正确答案）
        stmt = select(BankQuestion).where(BankQuestion.id.in_(sequence))
        result = db.execute(stmt)
        questions = {q.id: q for q in result.scalars().all()}

        wrong_questions_data = []
        
        # 🌟🌟🌟 新增：准备一个列表，用来装所有的做题记录（无论对错）
        practice_records_to_insert = []

        # 3. 逐题对比
        for q_id in sequence:
            q = questions.get(q_id)
            if not q: 
                continue

            # 兼容按字符串字典键或数字键传来的参数
            u_ans = user_answers_map.get(str(q_id)) or user_answers_map.get(q_id) or []
            c_ans = q.correct_answer

            # 判题逻辑（兼容多选集的无序比对与单选文本去除首尾空格比对）
            is_correct = False
            if isinstance(c_ans, list) and isinstance(u_ans, list):
                is_correct = set(c_ans) == set(u_ans)
            elif str(c_ans).strip() == str(u_ans).strip():
                is_correct = True
                
            # 🌟🌟🌟 新增：将每一道题的作答结果记录下来，存入明细表
            practice_records_to_insert.append(
                PracticeRecord(
                    user_id=user_id,
                    session_id=session_id,    
                    question_id=q_id,         
                    user_answer=u_ans,        
                    is_correct=is_correct,
                    is_completed=True         
                )
            )

            if not is_correct:
                wrong_questions_data.append({
                    "q_id": q_id,
                    "u_ans": u_ans,
                    "q_obj": q
                })

        # 🌟🌟🌟 新增：批量将做题记录真正写入数据库
        if practice_records_to_insert:
            db.add_all(practice_records_to_insert)

        # 4. 错题去重并写入数据库
        if wrong_questions_data:
            # 提取出所有的题号用于查重
            q_ids_to_check = [item["q_id"] for item in wrong_questions_data]
            
            exist_stmt = select(WrongQuestion.question_id).where(
                WrongQuestion.user_id == user_id,
                WrongQuestion.question_id.in_(q_ids_to_check)
            )
            exist_res = db.execute(exist_stmt)
            exist_ids = set(exist_res.scalars().all())

            # 在实例化 WrongQuestion 时，把题目快照内容塞进去
            new_wrong_objs = []
            for item in wrong_questions_data:
                if item["q_id"] not in exist_ids:
                    q_obj = item["q_obj"]
                    new_wrong_objs.append(
                        WrongQuestion(
                            user_id=user_id, 
                            question_id=item["q_id"],
                            question_content=q_obj.content,          # 补上题目内容快照
                            user_answer=item["u_ans"],               # 补上用户的错误答案
                            correct_answer=q_obj.correct_answer,     # 补上正确答案
                            ai_analysis=q_obj.ai_analysis            # 补上AI解析
                        )
                    )
            
            if new_wrong_objs:
                db.add_all(new_wrong_objs)

        # 5. 更新会话状态为已完成
        session.status = "completed"
        session.last_viewed_index = 0
        db.commit()
        
        return {"total": len(sequence), "wrong_count": len(wrong_questions_data)}

ps_service = PracticeSessionService()