# backend/models/users.py
from sqlalchemy import Column, String
from .database import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    wechat_openid = Column(String(128), nullable=False, unique=True, comment='微信用户唯一标识')
    nickname = Column(String(64), comment='用户昵称')
    avatar_url = Column(String(255), comment='头像链接')
    signature = Column(String(255), comment='个性签名')