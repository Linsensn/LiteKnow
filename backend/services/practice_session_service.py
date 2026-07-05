import csv
import json
from io import StringIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from crud import practice_sessions_crud
from utils.exceptions import CustomAPIException, ErrorCode
import random

class PracticeSessionService:
    async def start_new_session(self, db: AsyncSession, user_id: int, bank_id: int, mode: str, question_sequence: list):
        """核心业务：创建会话（根据模式混淆题目顺序）"""
        sequence = question_sequence.copy()
        if mode == "random":
            random.shuffle(sequence)
            
        try:
            obj_in = {
                "user_id": user_id, "bank_id": bank_id, 
                "practice_mode": mode, "question_sequence": sequence,
                "last_viewed_index": 0, "status": "ongoing"
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
        writer.writerow(["会话ID", "题库名称", "练习模式", "状态", "创建时间"])
        for s in sessions:
            b_name = s.bank.bank_name if hasattr(s, 'bank') and s.bank else "未知题库"
            writer.writerow([s.id, b_name, s.practice_mode, s.status, s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else ""])
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
                "status": row.get("状态", "ongoing"),
                "question_sequence": [],
                "last_viewed_index": 0
            })
        if objs_in:
            await practice_sessions_crud.create_multi_sessions(db=db, objs_in=objs_in)
            db.commit()

ps_service = PracticeSessionService()