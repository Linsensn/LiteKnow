# backend/schemas/schemas_user.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class WeChatLogin(BaseModel):
    code: str  # 小程序 wx.login() 获取的临时登录凭证

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "091xxxxxx123abc"
            }
        }
    )

class UserCreate(BaseModel):
    wechat_openid: Optional[str] = None # 管理员手动创建时可选
    nickname: str
    role: str = "student"
    is_active: bool = True

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "wechat_openid": "oUpF8uMuAJO_M2vd1Xje3OQNxLQs",
                "nickname": "张三",
                "role": "student",
                "is_active": True
            }
        }
    )


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    signature: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nickname": "李四",
                "avatar_url": "https://example.com/avatar/lisi.png",
                "signature": "好好学习，天天向上！"
            }
        }
    )

class UserStatusToggle(BaseModel):
    is_active: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_active": False
            }
        }
    )

class UserRoleUpdate(BaseModel):
    role: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "admin"
            }
        }
    )

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