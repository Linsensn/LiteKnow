# backend/schemas/ai_bank_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import json

class OptionItem(BaseModel):
    id: str = Field(..., description="选项标识，如 'A', 'B', 'C', 'D'")
    content: str = Field(..., description="选项的具体内容")

class BankParseRequest(BaseModel):
    bank_name: str = Field(..., description="要生成的题库名称")
    model_name: Optional[str] = Field(None, description="指定调用的大模型（不传则用系统默认）")
    content: Optional[str] = Field("", description="用户填写的纯文本内容或补充说明")
    # 🌟 对齐组长写法：前端可能以字符串形式传数组
    attachment_ids: str = Field("[]", description="已上传附件的ID列表(JSON数组字符串)，例如: [1, 2, 3]")

    # 🌟 对齐组长写法：提供一个属性直接获取解析好的列表
    @property
    def parsed_attachment_ids(self) -> List[int]:
        try:
            return json.loads(self.attachment_ids)
        except Exception:
            return []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_name": "高等数学期中复习题",
                "model_name": "deepseek-ai/DeepSeek-V3",
                "content": "请把这些照片里的题目提取出来",
                "attachment_ids": "[101, 102]"
            }
        }
    )

class ParsedQuestion(BaseModel):
    question_type: str = Field(..., description="题型: single_choice/multi_choice/essay/application 等")
    difficulty_level: str = Field(default="medium", description="难度: easy/medium/hard")
    content: str = Field(..., description="题干内容")
    options: List[OptionItem] = Field(default=[], description="选项列表对象数组，简答题等无选项请留空数组 []")
    correct_answer: List[str] = Field(..., description="正确答案(格式必须为数组，如 ['B'] 或 ['A','C']，简答题填关键得分点列表)")
    ai_analysis: str = Field(default="", description="AI生成的解析或原文自带的解析")

class BankParseOutputData(BaseModel):
    questions: List[ParsedQuestion] = Field(description="解析出的题目列表")

class BankParseResponse(BaseModel):
    bank_id: int = Field(..., description="生成的题库主键ID")
    bank_name: str = Field(..., description="题库名称")
    total_questions: int = Field(..., description="成功解析的题目数量")
    questions: List[ParsedQuestion] = Field(..., description="解析出的题目列表")