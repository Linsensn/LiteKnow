# backend/schemas/bank_questions.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime


class QuestionBase(BaseModel):
    bank_id: int = Field(..., description="所属题库ID")
    chapter_name: Optional[str] = Field(None, max_length=128, description="所属章节")
    question_type: str = Field(..., description="题型: single_choice/multi_choice/essay")
    difficulty_level: str = Field("medium", description="难度: easy/medium/hard")
    content: str = Field(..., description="题干内容")
    options_json: List[Any] = Field(default=[], description="选项列表，必须是数组格式")
    correct_answer: Any = Field(..., description="正确答案")
    ai_analysis: Optional[str] = None
    my_analysis: Optional[str] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    chapter_name: Optional[str] = None
    question_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    content: Optional[str] = None
    options_json: Optional[List[Any]] = None
    correct_answer: Optional[Any] = None
    ai_analysis: Optional[str] = None
    my_analysis: Optional[str] = None


class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)