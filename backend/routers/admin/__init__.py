
r"""
@Desc    : 管理员模块路由初始化
"""

from fastapi import APIRouter, Depends
# 修改这里的导入文件名
from . import question_banks_admin_router, sessions_admin_router, user_admin_router
from utils.deps import get_current_user, get_admin_user

# 创建专门针对 admin 模块的总 Router
admin_router = APIRouter(dependencies=[Depends(get_admin_user)] )

admin_router.include_router(user_admin_router.router)
admin_router.include_router(question_banks_admin_router.router)
admin_router.include_router(sessions_admin_router.router)
