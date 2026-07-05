from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# 请求：创建练习会话
class PracticeSessionCreate(BaseModel):
    bank_id: int = Field(..., description="要练习的题库ID")
    mode: str = Field(..., description="练习模式：sequential, random 等")
    question_ids: List[int] = Field(..., description="初始题号列表序列")

# 响应：单条练习会话信息
class PracticeSessionOut(BaseModel):
    id: int
    user_id: int
    bank_id: int
    practice_mode: str
    question_sequence: List[int]
    last_viewed_index: Optional[int]
    status: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

# 响应：携带题库详情的会话信息（用于列表渲染）
class PracticeSessionDetailOut(PracticeSessionOut):
    bank_name: Optional[str] = Field(None, description="冗余返回关联题库的名称")

# 请求：批量删除会话
class BatchDeleteSessionReq(BaseModel):
    ids: List[int] = Field(..., description="需要删除的会话ID列表")