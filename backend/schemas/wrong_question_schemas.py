from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# 请求：单条/批量外部导入错题
class WrongQuestionImport(BaseModel):
    question_content: str = Field(..., description="题目完整文本")
    source_image_url: Optional[str] = Field(None, description="原始拍照图片链接")
    user_answer: Optional[str] = Field(None, description="用户错误答案")
    correct_answer: Optional[str] = Field(None, description="正确答案")

# 请求：通用更新（含个人解析）
class WrongQuestionUpdate(BaseModel):
    question_content: Optional[str] = None
    my_analysis: Optional[str] = Field(None, description="学生自己撰写的反思与解析")
    user_answer: Optional[str] = None

# 请求：批量更新包裹
class BatchUpdateWrongQuestionsReq(BaseModel):
    ids: List[int] = Field(..., description="需要更新的错题ID列表")
    update_data: WrongQuestionUpdate = Field(..., description="统一更新的数据")

# 请求：批量删除错题
class BatchDeleteWrongQuestionsReq(BaseModel):
    ids: List[int] = Field(..., description="需要移出错题本的ID列表")

# 响应：错题本单条记录
class WrongQuestionOut(BaseModel):
    id: int
    user_id: int
    question_content: str
    source_image_url: Optional[str]
    user_answer: Optional[str]
    correct_answer: Optional[str]
    ai_analysis: Optional[str]
    my_analysis: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)