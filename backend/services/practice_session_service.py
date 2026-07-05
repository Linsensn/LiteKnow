from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from crud.crud_practice_sessions import practice_session
import random

class PracticeSessionService:
    async def start_new_session(self, db: AsyncSession, user_id: int, bank_id: int, mode: str, question_ids: list):
        # 业务规则：根据不同模式打乱或排序题号序列
        sequence = question_ids.copy()
        if mode == "random":
            random.shuffle(sequence)
            
        try:
            new_session = await practice_session.create(
                db=db, user_id=user_id, bank_id=bank_id, practice_mode=mode, question_sequence=sequence
            )
            await db.commit()
            return new_session
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_session_detail(self, db: AsyncSession, session_id: int, user_id: int):
        session = await practice_session.get(db=db, id=session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="会话不存在或无权限")
        return session

ps_service = PracticeSessionService()