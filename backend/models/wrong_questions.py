# backend/models/wrong_questions.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from .database import BaseModel

class WrongQuestion(BaseModel):
    __tablename__ = "wrong_questions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='关联用户ID')
    question_id = Column(Integer, ForeignKey("bank_questions.id", ondelete="SET NULL"), comment='关联的原题ID，方便追溯跳转')
    question_content = Column(Text, nullable=False, comment='题目完整文本')
    source_image_url = Column(String(255), comment='原始拍照图片链接')
    
    # 🌟 修改点：统一使用 JSON 格式，与练习记录和题库保持一致
    user_answer = Column(JSON, comment='用户错误答案(JSON格式)')
    correct_answer = Column(JSON, comment='正确答案(JSON格式)')
    
    ai_analysis = Column(Text, comment='AI深度解析')
    my_analysis = Column(Text, comment='我生成的解析')