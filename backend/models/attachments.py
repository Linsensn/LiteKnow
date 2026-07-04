# backend/models/attachments.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .database import BaseModel

class Attachment(BaseModel):
    __tablename__ = "attachments"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='上传者ID')
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), comment='绑定的消息ID')
    file_type = Column(String(64), comment='文件类型,如 image/jpeg')
    file_url = Column(String(255), nullable=False, comment='云端对象存储链接')
    extracted_text = Column(Text, comment='OCR或PDF解析出的纯文本')