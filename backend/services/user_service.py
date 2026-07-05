# backend/services/user_svc.py
import httpx
from sqlalchemy.orm import Session
from config.settings import settings
from utils.exceptions import CustomAPIException, ErrorCode 
from utils.security import create_access_token
from crud import user_crud

# 微信小程序配置（生产环境建议放入 .env）
WX_APPID = "your_appid_here"
WX_SECRET = "your_secret_here"

async def wechat_login_service(db: Session, code: str):
    """
    处理微信静默登录与自动注册业务
    """
    # 1. 调用微信服务端换取 OpenID
    wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={WX_APPID}&secret={WX_SECRET}&js_code={code}&grant_type=authorization_code"
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(wx_url)
        wx_data = resp.json()
        
    openid = wx_data.get("openid")
    if not openid:
        # 使用统一封装的业务异常抛出
        raise CustomAPIException(
            code=ErrorCode.WECHAT_AUTH_FAILED, 
            message=f"微信鉴权失败: {wx_data.get('errmsg', '无效的 code')}"
        )
        
    # 2. 查询用户，不存在则注册
    user = user_crud.get_user_by_openid(db, openid)
    if not user:
        user = user_crud.create_user(db, openid, role='student')
        
    # 3. 签发 JWT Token
    access_token = create_access_token(subject=user.id) #
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }