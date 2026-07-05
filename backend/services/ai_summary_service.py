# backend/services/ai_summary_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import logging

# 引入基础设施服务
from services.message_service import msg_service
from schemas.message_schema import MessageCreate

# 引入我们刚才封装好的统一大模型客户端
from utils.llm_client import llm_client 

logger = logging.getLogger("liteknow.ai_summary")

class AISummaryService:
    def __init__(self):
        # 将 Prompt 抽离，避免和业务逻辑耦合
        self.system_prompt = (
            "你是一个专业的学习助手。请仔细阅读用户提供的课本内容，"
            "自主分析并提取出核心主旨，同时生成详细的段落大意。"
            "请以清晰的Markdown列表格式返回。"
        )

    async def generate_text_summary_stream(
        self, db: AsyncSession, session_id: int, user_content: str
    ):
        try:
            # 1. 记录用户的输入到数据库 (复用已有的 MessageService)
            user_msg_in = MessageCreate(
                session_id=session_id,
                role="user",
                content_type="text",
                content=user_content
            )
            await msg_service.create_message(db, obj_in=user_msg_in)

            # 2. 调用大模型底层的流式接口
            llm_generator = llm_client.async_call_llm_stream(
                system_prompt=self.system_prompt,
                user_prompt=user_content
            )

            # 3. 构造代理生成器：边流式输出，边在内存中拼接，结束后持久化
            async def proxy_generator():
                full_ai_content = ""
                # 逐块消费底层模型的流
                async for chunk in llm_generator:
                    full_ai_content += chunk
                    yield chunk
                
                # 流输出彻底结束后，持久化 AI 的完整回答到数据库
                try:
                    ai_msg_in = MessageCreate(
                        session_id=session_id,
                        role="assistant",
                        content_type="text",
                        content=full_ai_content
                    )
                    await msg_service.create_message(db, obj_in=ai_msg_in)
                    logger.info(f"会话 {session_id} 的摘要消息已成功落库")
                except Exception as save_err:
                    logger.error(f"会话 {session_id} AI消息保存失败: {str(save_err)}")

            # 返回这个代理生成器给 Router 消费
            return proxy_generator()

        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"摘要生成请求失败: {str(e)}")

ai_summary_service = AISummaryService()