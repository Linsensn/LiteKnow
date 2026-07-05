from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert # MySQL 特有的 UPSERT 支持
from models.practice_records import PracticeRecord
from typing import List

class CRUDPracticeRecord:
    # 1. 新增或更新（Upsert）：利用联合唯一索引 uk_session_question 避免重复插入
    async def upsert(self, db: AsyncSession, *, session_id: int, user_id: int, question_id: int, user_answer: str, is_correct: bool):
        # insert 语句构建
        stmt = insert(PracticeRecord).values(
            session_id=session_id,
            user_id=user_id,
            question_id=question_id,
            is_completed=True,
            is_correct=is_correct,
            user_answer=user_answer
        )
        # 触发 Duplicate Key 时执行 Update (MySQL 特性)
        stmt = stmt.on_duplicate_key_update(
            is_completed=True,
            is_correct=is_correct,
            user_answer=user_answer
        )
        await db.execute(stmt)

    # 2. 查询单个会话下的所有答题记录 (渲染答题卡)
    async def get_by_session(self, db: AsyncSession, *, session_id: int) -> List[PracticeRecord]:
        stmt = select(PracticeRecord).where(PracticeRecord.session_id == session_id)
        result = await db.execute(stmt)
        return result.scalars().all()

practice_record = CRUDPracticeRecord()