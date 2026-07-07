# backend/routers/student/explain_router.py
"""
@Desc    : 知识精讲路由 — WebSocket 流式问答（适配微信小程序）
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

from config.database import get_db
from backend.services.ai_explain_service import explain_service

logger = logging.getLogger("liteknow.explain_ws")

router = APIRouter(prefix="/ai/explain", tags=["Student/AI/知识精讲"])


@router.websocket("/stream")
async def explain_websocket(
    websocket: WebSocket,
):
    await websocket.accept()
    # 在函数内部手动获取数据库会话
    async for db in get_db():
        break

    try:
        # 1. 前端发送 session_id 和 question
        data = await websocket.receive_text()
        req = json.loads(data)
        session_id = req["session_id"]
        question = req["question"]

        # 2. 调用 service 获取流式生成器
        generator = await explain_service.generate_explain_stream(
            db=db,
            session_id=session_id,
            question=question
        )

        # 3. 逐块推送给小程序
        async for chunk in generator:
            if chunk.startswith("data: "):
                chunk = chunk[6:].strip()

            if chunk == "[DONE]":
                await websocket.send_json({"type": "done"})
                break

            await websocket.send_text(chunk)

        await websocket.close()

    except WebSocketDisconnect:
        logger.info("小程序 WebSocket 断开连接")
    except Exception as e:
        logger.error(f"知识精讲 WebSocket 异常: {str(e)}")
        await websocket.send_json({"type": "error", "detail": str(e)})
        await websocket.close()