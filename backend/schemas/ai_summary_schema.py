# backend/schemas/ai_summary_schema.py
from pydantic import BaseModel, Field, ConfigDict

class SummaryRequest(BaseModel):
    session_id: int = Field(..., description="当前对话的会话ID")
    content: str = Field(..., description="用户提交的纯文本课文内容")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 1024,
                "content": "燕子去了，有再来的时候；杨柳枯了，有再青的时候；桃花谢了，有再开的时候..."
            }
        }
    )