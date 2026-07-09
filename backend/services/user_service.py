# backend/services/user_svc.py
import csv
import logging
from io import StringIO
import httpx
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from config.settings import settings
from utils.exceptions import CustomAPIException, ErrorCode 
from utils.security import create_access_token
from crud import user_crud

WX_APPID = settings.WX_APPID
WX_SECRET = settings.WX_SECRET

logger = logging.getLogger(__name__)

async def wechat_login_service(db: Session, code: str):
    """
    处理微信静默登录业务：
    - 普通用户：首次登录自动注册，赋予 'student' 角色。
    - 管理员：匹配数据库中预置的 openid，直接下发 'admin' 权限。
    """
    if code == "wx_o001":  # 测试管理员登录
        # 直接查库里写死的一个测试用户，或者动态创建一个
        user = user_crud.get_user_by_openid(db, code)
        if not user:
            user = user_crud.create_user(db, code, role='student')
        access_token = create_access_token(subject=user.id) 
        return access_token

    if code == "wx_o002":  # 测试管理员登录
        # 直接查库里写死的一个测试用户，或者动态创建一个
        user = user_crud.get_user_by_openid(db, code)
        if not user:
            user = user_crud.create_user(db, code, role='admin')
        access_token = create_access_token(subject=user.id) 
        return access_token

    # 调用微信服务端换取 OpenID
    wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={WX_APPID}&secret={WX_SECRET}&js_code={code}&grant_type=authorization_code"
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(wx_url)
        wx_data = resp.json()
        print(">>> 微信接口完整返回:", wx_data) # 临时添加这行代码
        
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

def audit_log(admin_id: int, action: str, details: str = ""):
    """【操作日志审计】记录管理员关键操作轨迹"""
    logger.info(f"[Admin Audit] AdminID:{admin_id} | Action:{action} | Detail:{details}")

async def export_users_csv(db: Session):
    """【数据导出】将用户表导出为 CSV 文件流"""
    # 提取全量未删除用户，生产环境通常会增加 limit 限制防止内存溢出
    users = user_crud.get_users_advanced(db, limit=50000)
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "OpenID", "Nickname", "Role", "Active Status", "Created At"])
    
    for u in users:
        writer.writerow([u.id, u.wechat_openid, u.nickname, u.role, "Active" if u.is_active else "Banned", u.created_at])
        
    output.seek(0)
    audit_log(admin_id=0, action="EXPORT_USERS", details=f"Exported {len(users)} users")
    
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )
