# backend/schemas/messages.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    session_id: int = Field(..., description="关联会话ID")
    role: str = Field(..., description="角色: user/assistant/system/tool")
    content_type: str = Field("text", description="内容类型: text/mixed")
    content: Optional[str] = Field(None, description="具体内容，mixed类型建议存JSON字符串")


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)