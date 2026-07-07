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
    ai_analysis: Optional[str] = Field(None, description="AI生成的分析")
    my_analysis: Optional[str] = Field(None, description="用户自定义解析")



class QuestionCreate(QuestionBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_id": 2001,
                "chapter_name": "进程管理",
                "question_type": "single_choice",
                "difficulty_level": "medium",
                "content": "以下哪个不是进程调度的算法？",
                "options_json": [
                    {"label": "A", "text": "FCFS"},
                    {"label": "B", "text": "LRU"},
                    {"label": "C", "text": "RR"},
                    {"label": "D", "text": "SJF"}
                ],
                "correct_answer": "B",
                "ai_analysis": "LRU是页面置换算法，不是进程调度算法。",
                "my_analysis": "需区分调度算法与置换算法。"
            }
        }
    )


class QuestionUpdate(BaseModel):
    chapter_name: Optional[str] = Field(None, description="所属章节")
    question_type: Optional[str] = Field(None, description="题型: single_choice/multi_choice/essay")
    difficulty_level: Optional[str] = Field(None, description="难度: easy/medium/hard")
    content: Optional[str] = Field(None, description="题干内容")
    options_json: Optional[List[Any]] = Field(None, description="选项列表，必须是数组格式")
    correct_answer: Optional[Any] = Field(None, description="正确答案")
    ai_analysis: Optional[str] = Field(None, description="AI生成的分析")
    my_analysis: Optional[str] = Field(None, description="用户自定义解析")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai_analysis": "更新后的AI解析内容",
                "my_analysis": "重新撰写的个人解析"
            }
        }
    )


class QuestionResponse(QuestionBase):
    id: int = Field(..., description="题目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 5001,
                "bank_id": 2001,
                "chapter_name": "进程管理",
                "question_type": "single_choice",
                "difficulty_level": "medium",
                "content": "以下哪个不是进程调度的算法？",
                "options_json": [
                    {"label": "A", "text": "FCFS"},
                    {"label": "B", "text": "LRU"},
                    {"label": "C", "text": "RR"},
                    {"label": "D", "text": "SJF"}
                ],
                "correct_answer": "B",
                "ai_analysis": "LRU是页面置换算法，不是进程调度算法。",
                "my_analysis": "需区分调度算法与置换算法。",
                "created_at": "2026-07-01T10:00:00",
                "updated_at": "2026-07-05T20:00:00"
            }
        }
    )