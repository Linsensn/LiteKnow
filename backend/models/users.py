# backend/models/users.py
from sqlalchemy import Column, String, Boolean
from .database import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    wechat_openid = Column(String(128), nullable=False, unique=True, comment='微信用户唯一标识')
    nickname = Column(String(64), comment='用户昵称')
    avatar_url = Column(String(255), comment='头像链接')
    role = Column(String(32), default='student', comment='用户角色: student/admin')
    signature = Column(String(255), comment='个性签名')
    is_active = Column(Boolean, default=True, comment='账号状态(True:正常/False:封禁)')
    is_deleted = Column(Boolean, default=False, comment='逻辑删除标志')