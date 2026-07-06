# backend/models/practice_sessions.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Text, Boolean
from .database import BaseModel

class PracticeSession(BaseModel):
    __tablename__ = "practice_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='用户ID')
    bank_id = Column(Integer, ForeignKey("question_banks.id", ondelete="CASCADE"), nullable=False, comment='所属题库ID')
    practice_mode = Column(String(32), nullable=False, comment='练习模式: sequential(顺序)/random(乱序)/mock(模拟考) 等')
    
    # 控制本次练习是否需要打乱选项
    is_options_shuffled = Column(Boolean, default=False, comment='是否开启选项乱序(防作弊/提高难度)')
    
    question_sequence = Column(JSON, nullable=False, comment='生成的题目ID序列(维持顺序)。顺序练习则按题库排序，乱序则随机打乱，如 [15, 2, 8, 33]')
    last_viewed_index = Column(Integer, default=0, comment='最后停留的题目数组索引，用于中断后恢复')
    status = Column(String(16), default='ongoing', comment='状态: ongoing进行中, completed已交卷')