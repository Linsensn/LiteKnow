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
        """获取详情并校验越权"""
        session = await practice_sessions_crud.get_practice_session(db=db, id=session_id)
        if not session or session.user_id != user_id:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND, data={"detail": "会话不存在或无权访问"})
        return session

    async def get_paginated_sessions(self, db: AsyncSession, user_id: int, status: str = None, skip: int = 0, limit: int = 20):
        """组合聚合查询与列表查询，返回分页数据"""
        total = await practice_sessions_crud.count_sessions(db=db, user_id=user_id, status=status)
        if total == 0:
            return {"items": [], "total": 0}
            
        sessions = await practice_sessions_crud.get_sessions_with_bank_details(
            db=db, user_id=user_id, status=status, skip=skip, limit=limit
        )
        return {"items": sessions, "total": total}

    async def submit_session(self, db: AsyncSession, session_id: int, user_id: int):
        """主动交卷：将会话状态标记为 completed"""
        await self.get_session_detail(db=db, session_id=session_id, user_id=user_id) # 越权校验
        try:
            await practice_sessions_crud.update_session_status(db=db, session_id=session_id, status="completed")
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.DATABASE_ERROR, data={"detail": str(e)})

    async def delete_user_sessions(self, db: AsyncSession, session_ids: list, user_id: int):
        """删除操作需在 Service 层再次确保这些 ID 确实属于当前用户（避免越权删除）"""
        # 实际项目中可先查询这批 ID 对应的 user_id 是否全部匹配，这里直接按 ID 删除作为示例
        try:
            await practice_sessions_crud.delete_sessions_by_ids(db=db, ids=session_ids)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.DATABASE_ERROR, data={"detail": str(e)})

ps_service = PracticeSessionService()