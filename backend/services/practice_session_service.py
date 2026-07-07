import csv
import random
from io import StringIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from crud import practice_sessions_crud
from models.bank_questions import BankQuestion
from utils.exceptions import CustomAPIException, ErrorCode

class PracticeSessionService:
    async def start_new_session(self, db: AsyncSession, user_id: int, bank_id: int, mode: str, is_options_shuffled: bool, question_sequence: list):
        """核心业务：创建会话（根据模式混淆题目顺序）"""
        sequence = question_sequence.copy() if question_sequence else []
        
        # 核心逻辑：如果前端传了空序列，后端根据 bank_id 主动查询所有题目ID
        if not sequence:
            stmt = select(BankQuestion.id).where(BankQuestion.bank_id == bank_id)
            result = db.execute(stmt)
            sequence = list(result.scalars().all())
            
        # 如果题库确实没题，直接抛错拦截
        if not sequence:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND, data={"detail": "该题库下暂时没有题目哦"})

        # 处理随机模式
        if mode == "random":
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

ps_service = PracticeSessionService()