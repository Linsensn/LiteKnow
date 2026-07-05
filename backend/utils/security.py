r"""
@Project : LiteKnow (教育助手)
@File    : backend\utils\security.py
@Desc    : 安全与加密工具模块，处理密码哈希校验及 JWT Token 签发。
"""

from datetime import datetime, timedelta 
from typing import Union, Any 
from jose import jwt 
from passlib.context import CryptContext 
from config.settings import settings 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与数据库中的哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password) 

def get_password_hash(password: str) -> str:
    """生成密码的 bcrypt 哈希值"""
    return pwd_context.hash(password) 

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """生成 JWT 访问令牌"""
    if expires_delta: 
        expire = datetime.utcnow() + expires_delta 
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) 
    
    to_encode = {"exp": expire, "sub": str(subject)} 
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM) 
    return encoded_jwt 