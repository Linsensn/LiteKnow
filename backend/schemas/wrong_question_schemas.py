from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

# 请求：更新个人错题解析
class WrongQuestionUpdateAnalysis(BaseModel):
    my_analysis: str = Field(..., description="学生自己撰写的反思与解析")

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