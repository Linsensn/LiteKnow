from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# 请求：提交单道题的作答 (保持原有业务)
class PracticeRecordSubmit(BaseModel):
    session_id: int = Field(..., description="当前关联的练习会话ID")
    question_id: int = Field(..., description="答题的题目ID")
    user_answer: str = Field(..., description="用户的选项或文本回答")
    correct_answer: str = Field(..., description="正确答案")
    question_content: str = Field(..., description="题干快照，用于错题本冗余展示")
    current_index: int = Field(..., description="该题目在序列中的位置索引，用于记录进度")

# 请求：单条新增
class PracticeRecordCreate(BaseModel):
    session_id: int = Field(..., description="练习会话ID")
    question_id: int = Field(..., description="题目ID")
    is_completed: bool = Field(default=False, description="是否已作答")
    is_correct: Optional[bool] = Field(default=None, description="是否正确")
    user_answer: Optional[str] = Field(default=None, description="用户作答内容")

# 请求：单条/批量更改
class PracticeRecordUpdate(BaseModel):
    is_completed: Optional[bool] = None
    is_correct: Optional[bool] = None
    user_answer: Optional[str] = None

# 请求：批量更新包裹
class BatchUpdateReq(BaseModel):
    ids: List[int] = Field(..., description="需要更新的记录ID列表")
    update_data: PracticeRecordUpdate = Field(..., description="统一更新的数据源")

# 请求：批量删除
class BatchDeleteReq(BaseModel):
    ids: List[int] = Field(..., description="需要删除的记录ID列表")

# 请求：状态切换
class StatusToggleReq(BaseModel):
    is_correct: bool = Field(..., description="更新后的正误状态")

# 响应：提交结果反馈
class SubmitResultOut(BaseModel):
    is_correct: bool

# 响应：单条答题记录详情
class PracticeRecordDetailOut(BaseModel):
    id: int
    session_id: int
    question_id: int
    is_completed: Optional[bool]
    is_correct: Optional[bool]
    user_answer: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)