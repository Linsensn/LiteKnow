# backend/models/question_banks.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .database import BaseModel

class QuestionBank(BaseModel):
    __tablename__ = "question_banks"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='创建者ID')
    bank_name = Column(String(128), nullable=False, comment='题库名称')
    description = Column(Text, comment='题库描述或学习计划')
    total_questions = Column(Integer, default=0, comment='总题数(方便快速查询)')