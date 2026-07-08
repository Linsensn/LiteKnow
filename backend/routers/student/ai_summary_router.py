# backend/routers/student/ai_summary_route.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from utils.deps import get_current_user

from schemas.ai_summary_schema import SummaryRequest
from services.ai_summary_service import ai_summary_service

router = APIRouter(prefix="/ai/summary", tags=["Student/AI/课本摘要"])

@router.post("/stream", summary="流式生成课本摘要")
async def create_text_summary_stream(
    req: SummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    处理纯文本格式的课文摘要请求。
    采用 Server-Sent Events (SSE) 协议返回打字机流式响应。
    """
    # 获取 service 返回的异步代理生成器，传入附件ID列表和用户ID
    generator = await ai_summary_service.generate_text_summary_stream(
        db=db, 
        session_id=req.session_id,
        user_id=current_student.id,  # 传递用户ID
        user_content=req.content,
        attachment_ids=req.parsed_attachment_ids # 传递解析好的附件ID列表
    )
    
    # 必须使用 StreamingResponse，并将 media_type 设为 text/event-stream
    return StreamingResponse(
        generator, 
        media_type="text/event-stream"
    )