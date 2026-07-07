# backend/schemas/ai_bank_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class BankParseRequest(BaseModel):
    bank_name: str = Field(..., description="要生成的题库名称")
    content: str = Field(..., description="用户上传的包含杂乱题目的纯文本内容")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_name": "高等数学期中复习题",
                "content": "1. 1+1等于几？ A. 1 B. 2 C. 3 D. 4 答案是B。解析：这是基础算术。"
            }
        }
    )

class ParsedQuestion(BaseModel):
    question_type: str = Field(..., description="题型: single_choice/multi_choice/essay 等")
    content: str = Field(..., description="题干内容")
    options: List[str] = Field(..., description="选项列表，如 ['A. 1', 'B. 2']")
    correct_answer: str = Field(..., description="正确答案")
    ai_analysis: str = Field(..., description="AI生成的解析或原文自带的解析")

class BankParseResponse(BaseModel):
    bank_id: int = Field(..., description="生成的题库主键ID")
    bank_name: str = Field(..., description="题库名称")
    total_questions: int = Field(..., description="成功解析的题目数量")
    questions: List[ParsedQuestion] = Field(..., description="解析出的题目列表")