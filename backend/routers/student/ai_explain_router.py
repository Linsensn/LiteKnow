# backend/routers/student/ai_explain_router.py
"""
@Desc    : 知识精讲路由 — HTTP SSE 流式问答 + 历史记录查询
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from utils.deps import get_current_user
from utils.response import success

from schemas.ai_explain_schema import ExplainRequest
from services.ai_explain_service import ai_explain_service
from services.message_service import msg_service

router = APIRouter(prefix="/ai/explain", tags=["Student/AI/知识精讲"])


@router.post("/stream", summary="流式知识精讲")
async def explain_stream(
    req: ExplainRequest,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    处理知识精讲请求，采用 SSE 协议返回打字机流式响应。

    Args:
        req (ExplainRequest): 包含 session_id（会话ID）和 question（提问内容）
        db: 数据库会话，通过依赖注入获取
        current_student: 当前登录用户信息，通过 JWT 认证获取

    Returns:
        StreamingResponse: SSE 格式的流式响应，前端按 data: {json} 逐块解析
    """

    generator = await ai_explain_service.generate_explain_stream(
        db=db,
        session_id=req.session_id,
        question=req.question
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream"
    )

@router.get("/history", summary="查询精讲历史记录")

async def get_explain_history(
    session_id: int = Query(..., description="精讲会话ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    查询指定会话的全部精讲问答历史记录（按时间正序排列）。

    Args:
        session_id: 会话ID，由前端先调用 POST /sessions 创建后获得
        db: 数据库会话，通过依赖注入获取
        current_student: 当前登录用户信息，通过 JWT 认证获取

    Returns:
        JSONResponse: 统一成功响应，data 为消息列表
    """
    messages = await msg_service.get_session_messages(
        db=db, session_id=session_id
    )

    return success(
        data=[msg.to_dict() if hasattr(msg, 'to_dict') else {
            "id": msg.id,
            "role": msg.role,
            "content_type": msg.content_type,
            "content": msg.content,
            "created_at": str(msg.created_at)
        } for msg in messages],
        message="精讲历史记录获取成功"
    )