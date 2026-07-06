# backend/schemas/explain_schema.py
from pydantic import BaseModel, Field, ConfigDict


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