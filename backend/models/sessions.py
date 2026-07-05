# backend/models/sessions.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from .database import BaseModel
from sqlalchemy.orm import relationship

class Session(BaseModel):
    __tablename__ = "sessions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='关联用户ID')
    title = Column(String(128), comment='会话标题(AI自动生成)')
    task_type = Column(String(64), comment='任务类型: 摘要/精讲/测验')

    parent_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, comment='父级会话ID')
    status = Column(String(32), default='active', comment='状态: active/archived')
    is_deleted = Column(Boolean, default=False, comment='逻辑删除标志')

    user = relationship("User", backref="sessions")