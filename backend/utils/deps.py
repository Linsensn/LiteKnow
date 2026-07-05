r"""
@Project : LiteKnow (教育助手)
@File    : backend\utils\deps.py
@Desc    : 全局依赖项定义模块，管理数据库连接、用户提取与角色鉴权。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError 
from sqlalchemy.orm import Session
from config.settings import settings 
from config.database import get_db 
from models.users import User
from utils.exceptions import HttpErrMsg 

# 设置 Swagger UI 的全局鉴权地址
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/student/auth/wechat") 

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """解析 JWT，获取当前登录的 User (可能是学生，也可能是管理员)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail=HttpErrMsg.UNAUTHORIZED, 
        headers={"WWW-Authenticate": "Bearer"}, 
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]) 
        user_id: str = payload.get("sub") 
        if user_id is None: 
            raise credentials_exception 
    except JWTError: 
        raise credentials_exception 
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None: 
        raise credentials_exception 
        
    return user 

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """在 get_current_user 的基础上进一步拦截，仅允许 admin 角色通行"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=HttpErrMsg.PERMISSION_DENIED
        )
    return current_user