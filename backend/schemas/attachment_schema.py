# backend/schemas/attachments.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class AttachmentCreate(BaseModel):
    file_type: str = Field(..., description="文件MIME类型，如 image/jpeg")
    file_url: str = Field(..., description="云端对象存储链接或本地相对路径")
    extracted_text: Optional[str] = Field(None, description="OCR或PDF解析出的纯文本")
    message_id: Optional[int] = Field(None, description="绑定的消息ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_type": "image/jpeg",
                "file_url": "https://oss.example.com/uploads/xxx.jpg",
                "extracted_text": "这是OCR识别出的文本内容",
                "message_id": 1024
            }
        }
    )
class AttachmentUpdate(BaseModel):
    file_type: Optional[str] = Field(None, description="文件MIME类型")
    file_url: Optional[str] = Field(None, description="文件存储路径")
    extracted_text: Optional[str] = Field(None, description="OCR或PDF解析出的纯文本")
    message_id: Optional[int] = Field(None, description="绑定的消息ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "extracted_text": "更新后的OCR识别文本",
                "message_id": 2048
            }
        }
    ) 
class AttachmentResponse(BaseModel):
    id: int = Field(..., description="附件ID")
    user_id: int = Field(..., description="上传者ID")
    message_id: Optional[int] = Field(None, description="绑定的消息ID")
    file_type: Optional[str] = Field(None, description="文件MIME类型")
    file_url: str = Field(..., description="云端对象存储链接或本地相对路径")
    extracted_text: Optional[str] = Field(None, description="OCR或PDF解析出的纯文本")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 8848,
                "message_id": 1024,
                "file_type": "image/jpeg",
                "file_url": "https://oss.example.com/uploads/xxx.jpg",
                "extracted_text": "OCR识别出的文本内容",
                "created_at": "2026-07-05T21:30:00"
            }
        }
    )