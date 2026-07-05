
r"""
@Desc    : 管理员模块路由初始化
"""

from fastapi import APIRouter, Depends
# 修改这里的导入文件名
from utils.deps import get_current_user, get_admin_user

# 创建专门针对 admin 模块的总 Router
admin_router = APIRouter(dependencies=[Depends(get_admin_user)] )

from . import (
    admin_admin_router,
    question_banks_admin_route,
    bank_question_admin_router,
    favorite_admin_router,
    attachment_admin_router,
    message_admin_router
)


admin_router.include_router(admin_admin_router.router)
admin_router.include_router(bank_question_admin_router.router)
admin_router.include_router(question_banks_admin_route.router)
admin_router.include_router(favorite_admin_router.router)
admin_router.include_router(attachment_admin_router.router)
admin_router.include_router(message_admin_router.router)