from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# 请求：单条创建练习会话
class PracticeSessionCreate(BaseModel):
    bank_id: int = Field(..., description="要练习的题库ID")
    practice_mode: str = Field(..., description="练习模式：sequential, random, mock 等")
    question_sequence: List[int] = Field(..., description="初始题号列表序列")

# 请求：单条/批量更改会话属性
class PracticeSessionUpdate(BaseModel):
    practice_mode: Optional[str] = None
    question_sequence: Optional[List[int]] = None
    last_viewed_index: Optional[int] = None
    status: Optional[str] = None

# 请求：批量更新包裹
class BatchUpdateSessionReq(BaseModel):
    ids: List[int] = Field(..., description="需要更新的会话ID列表")
    update_data: PracticeSessionUpdate = Field(..., description="统一更新的数据源")

# 请求：批量删除
class BatchDeleteSessionReq(BaseModel):
    ids: List[int] = Field(..., description="需要删除的会话ID列表")

# 请求：状态切换
class StatusToggleReq(BaseModel):
    status: str = Field(..., description="新状态，如 ongoing, completed")

# 响应：单条练习会话基础信息
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

# 响应：携带题库详情的会话信息（用于列表渲染和关联查询）
class PracticeSessionDetailOut(PracticeSessionOut):
    bank_name: Optional[str] = Field(None, description="关联查询：题库的名称")