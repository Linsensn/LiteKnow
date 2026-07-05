# backend/schemas/attachments.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AttachmentResponse(BaseModel):
    id: int = Field(..., description="附件ID")
    user_id: int = Field(..., description="上传者ID")
    message_id: Optional[int] = Field(None, description="绑定的消息ID")
    file_type: Optional[str] = Field(None, description="文件MIME类型")
    file_url: str = Field(..., description="云端对象存储链接或本地相对路径")
    extracted_text: Optional[str] = Field(None, description="OCR或PDF解析出的纯文本")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 