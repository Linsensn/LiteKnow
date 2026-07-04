from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from models.practice_sessions import PracticeSession
from typing import List, Optional

class CRUDPracticeSession:
    # 1. 创建练习会话，序列化 question_sequence
    async def create(self, db: AsyncSession, *, user_id: int, bank_id: int, practice_mode: str, question_sequence: list) -> PracticeSession:
        db_obj = PracticeSession(
            user_id=user_id,
            bank_id=bank_id,
            practice_mode=practice_mode,
            question_sequence=question_sequence,
            last_viewed_index=0,
            status="ongoing"
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    # 2. 获取单条会话详情，用于恢复练习进度
    async def get(self, db: AsyncSession, id: int) -> Optional[PracticeSession]:
        stmt = select(PracticeSession).where(PracticeSession.id == id)
        result = await db.execute(stmt)
        return result.scalar_first()

    # 3. 更新进度与状态 (例如交卷 completed)
    async def update_progress(self, db: AsyncSession, *, session_id: int, last_viewed_index: int, status: str = None):
        values = {"last_viewed_index": last_viewed_index}
        if status:
            values["status"] = status
        stmt = update(PracticeSession).where(PracticeSession.id == session_id).values(**values)
        await db.execute(stmt)

practice_session = CRUDPracticeSession()