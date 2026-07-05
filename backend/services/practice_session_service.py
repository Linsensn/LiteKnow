from sqlalchemy.ext.asyncio import AsyncSession
from crud import practice_sessions_crud
from utils.exceptions import CustomAPIException, ErrorCode
import random

class PracticeSessionService:
    async def start_new_session(self, db: AsyncSession, user_id: int, bank_id: int, mode: str, question_ids: list):
        # 业务规则：根据不同模式打乱或排序题号序列
        sequence = question_ids.copy()
        if mode == "random":
            random.shuffle(sequence)
            
        try:
            new_session = await practice_sessions_crud.create_practice_session(
                db=db, user_id=user_id, bank_id=bank_id, practice_mode=mode, question_sequence=sequence
            )
            await db.commit()
            return new_session
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(
                code=ErrorCode.PRACTICE_SESSION_CREATE_FAILED,
                data={"error_detail": str(e)}
            )

    async def get_session_detail(self, db: AsyncSession, session_id: int, user_id: int):
        session = await practice_sessions_crud.get_practice_session(db=db, id=session_id)
        if not session or session.user_id != user_id:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND)
        return session

ps_service = PracticeSessionService()