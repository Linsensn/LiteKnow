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
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 1024,
                "role": "user",
                "content_type": "text",
                "content": "牛顿第二定律的F=ma中，为什么质量越大加速度越小？"
            }
        }
    )

class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, description="更新后的消息内容")
    content_type: Optional[str] = Field(None, description="内容类型: text/mixed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "重新编辑后的消息内容",
                "content_type": "text"
            }
        }
    )

class MessageResponse(MessageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "session_id": 1024,
                "role": "user",
                "content_type": "text",
                "content": "牛顿第二定律的F=ma中，为什么质量越大加速度越小？",
                "created_at": "2026-07-05T21:30:00",
                "updated_at": "2026-07-05T21:30:00"
            }
        }
    )