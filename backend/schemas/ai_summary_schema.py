# backend/schemas/ai_summary_schema.py
from pydantic import BaseModel, Field

class SummaryRequest(BaseModel):
    session_id: int = Field(..., description="当前对话的会话ID")
    content: str = Field(..., description="用户提交的纯文本课文内容")