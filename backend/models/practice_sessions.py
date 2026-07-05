# backend/models/practice_sessions.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Text
from .database import BaseModel

class PracticeSession(BaseModel):
    __tablename__ = "practice_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='用户ID')
    bank_id = Column(Integer, ForeignKey("question_banks.id", ondelete="CASCADE"), nullable=False, comment='所属题库ID')
    practice_mode = Column(Text, nullable=False, comment='练习模式: sequential/random/mock 等')
    question_sequence = Column(JSON, nullable=False, comment='生成的题目ID序列(维持顺序)，如 [15, 2, 8, 33]')
    last_viewed_index = Column(Integer, default=0, comment='最后停留的题目数组索引，用于中断后恢复')
    status = Column(String(16), default='ongoing', comment='状态: ongoing进行中, completed已交卷')