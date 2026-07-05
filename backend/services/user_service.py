# backend/services/user_svc.py
import httpx
from sqlalchemy.orm import Session
from config.settings import settings
from utils.exceptions import CustomAPIException, ErrorCode 
from utils.security import create_access_token
from crud import user_crud

# 微信小程序配置（生产环境建议放入 .env）
WX_APPID = settings.WX_APPID
WX_SECRET = settings.WX_SECRET

async def wechat_login_service(db: Session, code: str):
    """
    处理微信静默登录业务：
    - 普通用户：首次登录自动注册，赋予 'student' 角色。
    - 管理员：匹配数据库中预置的 openid，直接下发 'admin' 权限。
    """
    # 调用微信服务端换取 OpenID
    wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={WX_APPID}&secret={WX_SECRET}&js_code={code}&grant_type=authorization_code"
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(wx_url)
        wx_data = resp.json()
        
    openid = wx_data.get("openid")
    if not openid:
        raise CustomAPIException(code=ErrorCode.WECHAT_AUTH_FAILED)

    # 2. 查询用户，不存在则注册
    user = user_crud.get_user_by_openid(db, openid)
    if not user:
        user = user_crud.create_user(db, openid, role='student')
        
    # 3. 签发 JWT Token
    access_token = create_access_token(subject=user.id) #
 
    # 如果不存在，说明是全新的普通学生用户，走自动注册逻辑
    if not user:
        user = user_crud.create_user(db, openid, role='student')
        
    # 签发 JWT Token
    access_token = create_access_token(subject=user.id) 
    
    # 返回的 role 是动态的！管理员登录会返回 'admin'，学生登录返回 'student'
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }