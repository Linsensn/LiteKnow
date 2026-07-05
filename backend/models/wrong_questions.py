# backend/models/wrong_questions.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .database import BaseModel

class WrongQuestion(BaseModel):
    __tablename__ = "wrong_questions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='关联用户ID')
    # 关联到bank_questions表的题目ID，方便追溯原题
    question_content = Column(Text, nullable=False, comment='题目完整文本')
    source_image_url = Column(String(255), comment='原始拍照图片链接')
    user_answer = Column(String(255), comment='用户错误答案')
    correct_answer = Column(String(255), comment='正确答案')
    ai_analysis = Column(Text, comment='AI深度解析')
    my_analysis = Column(Text, comment='我生成的解析')
