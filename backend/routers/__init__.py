
r"""
@Desc    : 微模块路由初始化
"""

from fastapi import APIRouter, Depends
from .admin import admin_router
from .student import student_router
from .system import router as system_router
from utils.deps import get_current_user, get_admin_user

root_router = APIRouter()

root_router.include_router(admin_router, prefix="/admin",)
root_router.include_router(student_router, prefix="/student",)
root_router.include_router(system_router)

