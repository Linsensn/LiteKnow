# backend/schemas/schemas_user.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class WeChatLogin(BaseModel):
    code: str  # 小程序 wx.login() 获取的临时登录凭证

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    signature: Optional[str] = None

class UserOut(BaseModel):
    id: int
    nickname: Optional[str]
    avatar_url: Optional[str]
    signature: Optional[str]
    role: str
    
    model_config = ConfigDict(from_attributes=True) # 允许从 ORM 模型转换