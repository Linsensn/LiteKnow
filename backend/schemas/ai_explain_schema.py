# backend/schemas/explain_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ExplainRequest(BaseModel):
    session_id: int = Field(..., description="精讲会话ID")
    question: str = Field(..., description="用户提出的问题")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 1024,
                "question": "牛顿第二定律的F=ma中，为什么质量越大加速度越小？"
            }
        }
    )

class ExplainResponse(BaseModel):
    id: int = Field(..., description="精讲记录ID")
    session_id: int = Field(..., description="关联会话ID")
    question: str = Field(..., description="用户提出的问题")
    answer: str = Field(..., description="AI生成的精讲回答")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "session_id": 1024,
                "question": "牛顿第二定律的F=ma中，为什么质量越大加速度越小？",
                "answer": "根据牛顿第二定律F=ma，当合外力F一定时，加速度a与质量m成反比...",
                "created_at": "2026-07-05T21:30:00"
            }
        }
    )