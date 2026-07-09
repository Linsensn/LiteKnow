# backend/schemas/ai_summary_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import json

class SummaryRequest(BaseModel):
    session_id: int = Field(..., description="当前对话的会话ID")
    content: str = Field(..., description="用户提交的纯文本课文内容")
    attachment_ids: str = Field("[]", description="已上传附件的ID列表(JSON数组字符串)，例如: [1, 2, 3]")

    # 提供一个属性直接获取解析好的列表
    @property
    def parsed_attachment_ids(self) -> List[int]:
        try:
            return json.loads(self.attachment_ids)
        except Exception:
            return []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 1024,
                "content": "燕子去了，有再来的时候...",
                "attachment_ids": "[1, 2]"
            }
        }
    )