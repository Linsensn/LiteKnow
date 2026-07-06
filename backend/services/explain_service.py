# backend/services/explain_service.py
"""
@Desc    : 知识精讲服务 — 多轮对话式答疑
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import logging
import json

from services.message_service import msg_service
from schemas.message_schema import MessageCreate
from utils.llm_client import llm_client

logger = logging.getLogger("liteknow.explain")

class ExplainService:
    def __init__(self):
        self.system_prompt = (
            "你是一位耐心、专业的学科教师。请用通俗易懂的语言解答学生提出的问题。\n"
            "回答时请做到：\n"
            "1. 先给出简洁的核心结论\n"
            "2. 再展开详细解释原理\n"
            "3. 适当举例帮助理解\n"
            "4. 如果学生的问题有歧义，先澄清再回答\n"
            "请以清晰的Markdown格式返回。"
        )
        # 限制携带的最大历史消息数（20轮对话 = 40条）
        self.max_history_messages = 40

    async def generate_explain_stream(
        self, db: AsyncSession, session_id: int, question: str
    ):
        try:
            # 1. 记录用户问题到数据库
            user_msg = MessageCreate(
                session_id=session_id,
                role="user",
                content_type="text",
                content=question
            )
            await msg_service.create_message(db, obj_in=user_msg)

            # 2. 拉取该会话全部历史消息
            history = await msg_service.get_session_messages(db, session_id=session_id)

            # 3. 截取最近 N 条作为上下文，防止 token 超限
            chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in history[-self.max_history_messages:]
            ]

            # 4. 调用带上下文的流式对话
            llm_generator = llm_client.async_call_chat_stream(
                system_prompt=self.system_prompt,
                messages=chat_history
            )

            # 5. SSE 代理生成器（与摘要服务一致）
            async def proxy_generator():
                full_ai_content = ""
                async for chunk in llm_generator:
                    full_ai_content += chunk
                    safe_chunk = json.dumps({"content": chunk}, ensure_ascii=False)
                    yield f"data: {safe_chunk}\n\n"

                yield "data: [DONE]\n\n"

                # 流结束后，持久化 AI 完整回答
                try:
                    ai_msg = MessageCreate(
                        session_id=session_id,
                        role="assistant",
                        content_type="text",
                        content=full_ai_content
                    )
                    await msg_service.create_message(db, obj_in=ai_msg)
                    logger.info(f"精讲会话 {session_id} AI回答已落库")
                except Exception as save_err:
                    logger.error(f"精讲会话 {session_id} AI回答保存失败: {save_err}")

            return proxy_generator()

        except Exception as e:
            logger.error(f"知识精讲生成失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"知识精讲请求失败: {str(e)}")


explain_service = ExplainService()