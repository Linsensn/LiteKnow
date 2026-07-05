# backend/models/favorites.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .database import BaseModel

class Favorite(BaseModel):
    __tablename__ = "favorites"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='关联用户ID')
    content_type = Column(String(64), nullable=False, comment='收藏类型: 摘要/题目')
    cover_image_url = Column(String(255), comment='列表展示用的封面/缩略图')
    # 根据收藏的类型，存关联的id（摘要/知识点/题目）（message,bank_questions） 
    content_id = Column(Integer, nullable=False, comment='关联的源数据ID，配合content_type对应不同表')
    source_session = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), comment='来源会话ID, 方便追溯')