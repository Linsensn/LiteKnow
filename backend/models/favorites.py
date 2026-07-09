# backend/models/favorites.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from .database import BaseModel

class Favorite(BaseModel):
    __tablename__ = "favorites"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='关联用户ID')
    content_type = Column(String(64), nullable=False, comment='收藏类型枚举: question/summary/session/bank')
    cover_image_url = Column(String(255), comment='列表展示用的封面/缩略图')
    # 根据收藏的类型，存关联的id（question→bank_questions, summary→messages, session→sessions, bank→question_banks）
    content_ids = Column(JSON, nullable=False, default=list, comment='收藏的内容ID数组，对应content_type关联不同业务表')
    source_session = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), comment='来源会话ID, 方便追溯')