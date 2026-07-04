
r"""
@Desc    : 微信小程序学生端模块路由初始化
"""

from fastapi import APIRouter, Depends
# 修改这里的导入文件名
from . import (
    student_student_router, 
    question_banks_student_route, 
    wrong_questions_route, 
    practice_sessions_route, 
    practice_records_route
)
from utils.deps import get_current_user, get_admin_user

student_router = APIRouter(dependencies=[Depends(get_current_user)])

# 挂载学生视角的学习与练习路由，同步修改名称
student_router.include_router(student_student_router.router)
student_router.include_router(question_banks_student_route.router)
student_router.include_router(wrong_questions_route.router)
student_router.include_router(practice_sessions_route.router)
student_router.include_router(practice_records_route.router)

