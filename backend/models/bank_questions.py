# backend/models/bank_questions.py
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from .database import BaseModel

class BankQuestion(BaseModel):
    __tablename__ = "bank_questions"
    
    bank_id = Column(Integer, ForeignKey("question_banks.id", ondelete="CASCADE"), nullable=False, comment='所属题库ID')
    chapter_name = Column(String(128), comment='所属章节(用于支持"章节练习")')
    question_type = Column(String(32), nullable=False, comment='题型: single_choice/multi_choice/essay 等(支持"题型练习")')
    difficulty_level = Column(String(32), default='medium', comment='难度: easy/medium/hard (支持"难度练习")')
    content = Column(Text, nullable=False, comment='题干内容')
    options_json = Column(JSON, comment='选项列表(JSON格式,如 ["A. 选项1", "B. 选项2"])')
    correct_answer = Column(String(255), nullable=False, comment='正确答案')
    ai_analysis = Column(Text, comment='AI生成的解析')
    my_analysis = Column(Text, comment='我生成的解析')