# backend/schemas/schemas_user.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class WeChatLogin(BaseModel):
    code: str  # 小程序 wx.login() 获取的临时登录凭证

class UserCreate(BaseModel):
    wechat_openid: Optional[str] = None # 管理员手动创建时可选
    nickname: str
    role: str = "student"
    is_active: bool = True

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    signature: Optional[str] = None

class UserStatusToggle(BaseModel):
    is_active: bool

class UserRoleUpdate(BaseModel):
    role: str

class UserOut(BaseModel):
    id: int 
    wechat_openid: Optional[str]
    nickname: Optional[str] 
    avatar_url: Optional[str] 
    signature: Optional[str] 
    role: str 
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)