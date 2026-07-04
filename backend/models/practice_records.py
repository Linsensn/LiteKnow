# backend/models/practice_records.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from .database import BaseModel

class PracticeRecord(BaseModel):
    __tablename__ = "practice_records"
    
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False, comment='关联的练习会话ID')
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='用户ID')
    question_id = Column(Integer, ForeignKey("bank_questions.id", ondelete="CASCADE"), nullable=False, comment='题目ID')
    is_completed = Column(Boolean, default=False, comment='是否已作答(用来渲染答题卡)')
    is_correct = Column(Boolean, comment='是否正确(未作答时为空)')
    user_answer = Column(String(255), comment='用户实际作答内容')

    # 添加联合唯一索引约束
    __table_args__ = (
        UniqueConstraint('session_id', 'question_id', name='uk_session_question'),
    )