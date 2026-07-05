from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# 请求：外部批量导入错题
class WrongQuestionImport(BaseModel):
    question_id: Optional[int] = Field(None, description="关联的题库原题ID")
    question_content: str = Field(..., description="题目完整文本")
    source_image_url: Optional[str] = Field(None, description="原始拍照图片链接")
    user_answer: Optional[str] = Field(None, description="用户错误答案")
    correct_answer: Optional[str] = Field(None, description="正确答案")

# 请求：更新个人错题解析
class WrongQuestionUpdateAnalysis(BaseModel):
    my_analysis: str = Field(..., description="学生自己撰写的反思与解析")

# 请求：批量删除错题
class BatchDeleteWrongQuestionsReq(BaseModel):
    ids: List[int] = Field(..., description="需要移出错题本的ID列表")

# 响应：错题本单条记录
class WrongQuestionOut(BaseModel):
    id: int
    user_id: int
    question_id: Optional[int] = Field(None, description="关联的原题ID，可跳转追溯")
    question_content: str
    source_image_url: Optional[str]
    user_answer: Optional[str]
    correct_answer: Optional[str]
    ai_analysis: Optional[str]
    my_analysis: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)