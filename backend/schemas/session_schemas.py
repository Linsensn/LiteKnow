# backend/schemas/session_schemas.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class SessionBase(BaseModel):
    title: str
    task_type: str
    parent_id: Optional[int] = None  # 用于支持【树形查询】
    status: Optional[str] = "active" # active, archived

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    task_type: Optional[str] = None
    status: Optional[str] = None

class SessionStatusToggle(BaseModel):
    status: str

# 【关联查询】返回体：嵌套 User 信息
class UserSimpleOut(BaseModel):
    id: int
    nickname: Optional[str]

class SessionOut(SessionBase):
    id: int
    user_id: int
    is_deleted: bool
    created_at: datetime
    user: Optional[UserSimpleOut] = None # 用于承接关联查询结果
    
    model_config = ConfigDict(from_attributes=True)

# 【树形查询】返回体
class SessionTreeOut(SessionOut):
    children: List['SessionTreeOut'] = []