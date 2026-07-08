# backend/utils/llm_client.py
import os
import logging
from config.settings import settings
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI

# 配置简单的日志记录
logger = logging.getLogger("liteknow.llm")

# 加载 .env 环境变量
load_dotenv()

class LLMClient:
    def __init__(self):
        self.enabled = settings.LLM_ENABLED
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL

        # 优先读取系统配置的默认模型，如果没配则降级到智谱
        self.model_name = getattr(
            settings, 
            "LLM_DEFAULT_MODEL", 
            getattr(settings, "LLM_MODEL_ZHIPU", "THUDM/GLM-Z1-9B-0414")
        )

        self.client = None
        if self.enabled and self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"LLM Client 初始化成功，当前模型: {self.model_name}")
        else:
            logger.warning("LLM Client 未启用或缺少 API_KEY。")

    async def async_call_llm_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        """
        流式请求 (Streaming)
        适用于：知识精讲、课文摘要等需要给前端展示“打字机”效果的场景。
        使用 yield 逐块返回字符串。
        """
        if not self.enabled or not self.client:
            yield "大模型未配置或未启用。"
            return

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                stream=True  # 核心参数：开启流式输出
            )
            
            async for chunk in response:
                # 提取增量文本
                delta_content = chunk.choices[0].delta.content
                if delta_content:
                    yield delta_content
                    
        except Exception as e:
            logger.error(f"LLM 流式调用异常: {str(e)}")
            yield f"\n[服务异常: {str(e)}]"

    async def async_call_llm(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_format: str = "text",
        target_model: str = None 
    ) -> str:
        """
        非流式请求 (Blocking/Normal)
        适用于：智能测验、题库整理等需要大模型一次性输出完整 JSON 结构化数据的场景。
        """
        """非流式请求"""
        if not self.enabled or not self.client:
            return "大模型未配置或未启用。"
            
        # 如果调用时没传，就用系统默认的模型
        actual_model = target_model if target_model else self.model_name

        try:
            kwargs = {
                "model": actual_model, # 使用动态决定的模型
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3, # 结构化任务建议调低温度以保证输出稳定性
                "stream": False
            }
            
            # 如果平台支持且需要强制输出 JSON，可传入 response_format="json_object"
            if response_format == "json_object":
                kwargs["response_format"] = {"type": "json_object"}

            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
            
        except Exception as e:
            logger.error(f"LLM 非流式调用异常: {str(e)}")
            return f"LLM 调用异常: {str(e)}"

    async def async_call_llm_stream(
        self, 
        system_prompt: str, 
        user_prompt: str,
        target_model: str = None 
    ) -> AsyncGenerator[str, None]:
        if not self.enabled or not self.client:
            yield "大模型未配置或未启用。"
            return

        actual_model = target_model if target_model else self.model_name

        try:
            response = await self.client.chat.completions.create(
                model=actual_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                stream=True
            )

            async for chunk in response:
                delta_content = chunk.choices[0].delta.content
                if delta_content:
                    yield delta_content

        except Exception as e:
            logger.error(f"LLM 对话流式调用异常: {str(e)}")
            yield f"\n[服务异常: {str(e)}]"

    def get_langchain_chat_model(model_name: str = None, temperature: float = 0.3) -> ChatOpenAI:
        """
        获取配置好的 LangChain ChatOpenAI 实例
        """
        # 优先读取传入的模型，其次读取默认模型
        actual_model = model_name or getattr(
            settings, "LLM_DEFAULT_MODEL", 
            getattr(settings, "LLM_MODEL_ZHIPU", "THUDM/GLM-Z1-9B-0414")
        )
        
        return ChatOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=actual_model,
            temperature=temperature,
            max_retries=2  # 如果网络抖动，允许 LangChain 自动重试 2 次
        )
# 实例化单例，整个项目只需 from utils.llm_client import llm_client 即可调用
llm_client = LLMClient()