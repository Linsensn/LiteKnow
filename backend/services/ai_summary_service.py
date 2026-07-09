# backend/services/ai_summary_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import logging
import json # 引入 json 用于序列化
from typing import List

# 引入基础设施服务
from services.message_service import msg_service
from schemas.message_schema import MessageCreate
from services.attachment_service import att_service # 引入附件服务
from crud.messages_crud import msg_crud

# 引入我们刚才封装好的统一大模型客户端
from utils.llm_client import llm_client 
from models.messages import Message 

logger = logging.getLogger("liteknow.ai_summary")

class AISummaryService:
    def __init__(self):
        self.system_prompt = (
            "你是一个专业的学习助手。请仔细阅读用户提供的课本内容，"
            "自主分析并提取出核心主旨，同时生成详细的段落大意。"
            "请以清晰的Markdown列表格式返回。"
        )

    async def generate_text_summary_stream(
        self, db: AsyncSession, session_id: int, user_id: int, user_content: str, attachment_ids: List[int] = None
    ):
        try:
            # ----- 1. 拼接【用户文本 + 附件提取文本】 -----
            content_parts = [user_content]
            if attachment_ids:
                for att_id in attachment_ids:
                    # 传入 user_id 确保权限校验安全
                    att = await att_service.get_attachment_by_id(db, att_id=att_id, user_id=user_id) 
                    if att and att.extracted_text and att.extracted_text.strip():
                        content_parts.append(f"【附件内容】:\n{att.extracted_text}")
            
            final_user_content = "\n\n".join(content_parts)

            # ----- 2. 记录用户的**合并后**的输入到数据库 -----
            user_msg_in = MessageCreate(
                session_id=session_id,
                role="user",
                content_type="text",
                content=final_user_content # 这里要记录带附件内容的完整输入
            )
            await msg_service.create_message(db, obj_in=user_msg_in)

            history_messages = await msg_crud.get_by_session(db, session_id)

            # 构造符合大模型要求的格式 [{'role': 'user', 'content': '...'}, ...]
            history_payload = [
                {"role": msg.role, "content": msg.content} 
                for msg in history_messages
            ]

            # ----- 4. 调用大模型的多轮对话流式接口 -----
            # 使用 async_call_chat_stream 替换 async_call_llm_stream
            llm_generator = llm_client.async_call_chat_stream(
                system_prompt=self.system_prompt,
                messages=history_payload 
            )

            # ----- 5. 构造代理生成器：严格适配小程序的 SSE 格式 -----
            async def proxy_generator():
                full_ai_content = ""
                async for chunk in llm_generator:
                    full_ai_content += chunk
                    safe_chunk = json.dumps({"content": chunk}, ensure_ascii=False)
                    yield f"data: {safe_chunk}\n\n"
                
                yield "data: [DONE]\n\n"
                
                # 流输出彻底结束后，持久化 AI 的完整回答
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

            return proxy_generator()

        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"摘要生成请求失败: {str(e)}")

ai_summary_service = AISummaryService()