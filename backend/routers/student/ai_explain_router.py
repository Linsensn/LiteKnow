# backend/routers/student/ai_explain_router.py
"""
@Desc    : 知识精讲路由 — HTTP SSE 流式问答（适配微信小程序）
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from utils.deps import get_current_user

from schemas.ai_explain_schema import ExplainRequest
from services.ai_explain_service import explain_service

router = APIRouter(prefix="/ai/explain", tags=["Student/AI/知识精讲"])


@router.post("/stream", summary="流式知识精讲")
async def explain_stream(
    req: ExplainRequest,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    处理知识精讲请求。
    采用 Server-Sent Events (SSE) 协议返回打字机流式响应。
    """
    generator = await explain_service.generate_explain_stream(
        db=db,
        session_id=req.session_id,
        question=req.question
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream"
    )