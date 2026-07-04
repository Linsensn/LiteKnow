# backend/models/messages.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .database import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"
    
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, comment='关联会话ID')
    role = Column(String(32), nullable=False, comment='角色: user/assistant/system/tool')
    content_type = Column(String(32), default='text', comment='内容类型: text/mixed')
    content = Column(Text, comment='具体内容(mixed时建议存JSON)')