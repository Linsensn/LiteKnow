from fastapi import APIRouter
from . import admin_admin_router
from utils.deps import get_current_user, get_admin_user

# 创建一个专门针对 admin 模块的总 Router
admin_router = APIRouter()

# 把细分的路由挂载到总路由上
admin_router.include_router(admin_admin_router.router)
