# backend/models/sessions.py
from sqlalchemy import Column, Integer, String, ForeignKey
from .database import BaseModel

class Session(BaseModel):
    __tablename__ = "sessions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='关联用户ID')
    title = Column(String(128), comment='会话标题(AI自动生成)')
    task_type = Column(String(64), comment='任务类型: 摘要/精讲/测验')