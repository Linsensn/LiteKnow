# backend/models/practice_records.py
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, UniqueConstraint
from .database import BaseModel

class PracticeRecord(BaseModel):
    __tablename__ = "practice_records"
    
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False, comment='关联的练习会话ID')
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='用户ID')
    question_id = Column(Integer, ForeignKey("bank_questions.id", ondelete="CASCADE"), nullable=False, comment='题目ID')
    is_completed = Column(Boolean, default=False, comment='是否已作答(用来渲染答题卡)')
    is_correct = Column(Boolean, comment='是否正确(未作答时为空, 简答题可扩展支持小数得分)')
    
    # 记录这道题展示给用户时的选项顺序
    option_sequence = Column(JSON, comment='(选项乱序时使用)展示的选项ID顺序，如 ["C", "A", "D", "B"]，未打乱则为空或等于原始顺序')
    
    # 用户作答改为JSON，结构与 correct_answer 保持对应
    user_answer = Column(JSON, comment='用户实际作答内容(JSON格式)。详见下方数据格式说明')

    __table_args__ = (
        UniqueConstraint('session_id', 'question_id', name='uk_session_question'),
    )