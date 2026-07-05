from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# 请求：提交单道题的作答
class PracticeRecordSubmit(BaseModel):
    session_id: int = Field(..., description="当前关联的练习会话ID")
    question_id: int = Field(..., description="答题的题目ID")
    user_answer: str = Field(..., description="用户的选项或文本回答")
    correct_answer: str = Field(..., description="正确答案比令人识")
    question_content: str = Field(..., description="题干快照，用于错题本冗余展示")
    current_index: int = Field(..., description="该题目在序列中的位置索引，用于记录进度")

# 响应：提交结果反馈
class SubmitResultOut(BaseModel):
    is_correct: bool

# 响应：单条答题记录详情
class PracticeRecordDetailOut(BaseModel):
    id: int
    session_id: int
    question_id: int
    is_completed: bool
    is_correct: Optional[bool]
    user_answer: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# 请求：批量删除
class BatchDeleteReq(BaseModel):
    ids: List[int] = Field(..., description="需要删除的记录ID列表")

# 请求：状态切换
class StatusToggleReq(BaseModel):
    is_correct: bool = Field(..., description="更新后的正误状态")