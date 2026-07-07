# backend/schemas/ai_bank_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Any

# 新增：定义严格的选项结构
class OptionItem(BaseModel):
    id: str = Field(..., description="选项标识，如 'A', 'B', 'C', 'D'")
    content: str = Field(..., description="选项的具体内容")

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
    question_type: str = Field(..., description="题型: single_choice/multi_choice/essay/application 等")
    difficulty_level: str = Field(default="medium", description="难度: easy/medium/hard")
    content: str = Field(..., description="题干内容")
    options: List[OptionItem] = Field(default=[], description="选项列表对象数组")
    # 修改：适配数据库的 JSON 类型
    correct_answer: Any = Field(..., description="正确答案(JSON格式，选择题推荐使用数组如 ['B'] 或 ['A','C'])")
    ai_analysis: str = Field(default="", description="AI生成的解析或原文自带的解析")

class BankParseResponse(BaseModel):
    bank_id: int = Field(..., description="生成的题库主键ID")
    bank_name: str = Field(..., description="题库名称")
    total_questions: int = Field(..., description="成功解析的题目数量")
    questions: List[ParsedQuestion] = Field(..., description="解析出的题目列表")