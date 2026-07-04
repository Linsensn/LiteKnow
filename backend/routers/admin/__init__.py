r"""
@Desc    : 管理员模块路由初始化
"""

from fastapi import APIRouter
# 修改这里的导入文件名
from . import question_banks_admin_route

# 创建专门针对 admin 模块的总 Router
admin_router = APIRouter()

# 挂载管理员视角的题库路由，也要同步修改这里的名称
admin_router.include_router(question_banks_admin_route.router)

# 如果有其他路由，继续 append...