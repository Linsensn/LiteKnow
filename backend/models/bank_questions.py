# backend/models/bank_questions.py
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from .database import BaseModel

class BankQuestion(BaseModel):
    __tablename__ = "bank_questions"
    
    bank_id = Column(Integer, ForeignKey("question_banks.id", ondelete="CASCADE"), nullable=False, comment='所属题库ID')
    chapter_name = Column(String(128), comment='所属章节(用于支持"章节练习")')
    question_type = Column(String(32), nullable=False, comment='题型: single_choice(单选)/multi_choice(多选)/essay(简答)/application(应用题) 等')
    difficulty_level = Column(String(32), default='medium', comment='难度: easy/medium/hard')
    content = Column(Text, nullable=False, comment='题干内容')
    options_json = Column(JSON, comment='选项列表(JSON格式)。规范：[{"id": "A", "content": "选项1"}, {"id": "B", "content": "选项2"}]')
    correct_answer = Column(JSON, nullable=False, comment='正确答案(JSON格式)。详见下方数据格式说明')
    ai_analysis = Column(Text, comment='AI生成的解析')
    my_analysis = Column(Text, comment='我生成的解析')