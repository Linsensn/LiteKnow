
r"""
@Desc    : 微信小程序学生端模块路由初始化
"""

from fastapi import APIRouter, Depends
from utils.deps import get_current_user, get_admin_user
student_router = APIRouter(dependencies=[Depends(get_current_user)])

# 修改这里的导入文件名
from . import (
    practice_records_student_router,
    practice_sessions_student_router,
    question_banks_student_router,
    student_student_router, 
    bank_question_student_router,
    favorite_student_router,
    attachment_student_router,
    message_student_router,
    wrong_questions_student_router
)

# 挂载学生视角的学习与练习路由，同步修改名称
student_router.include_router(student_student_router.router)
student_router.include_router(bank_question_student_router.router)
student_router.include_router(favorite_student_router.router)
student_router.include_router(attachment_student_router.router)
student_router.include_router(message_student_router.router)
student_router.include_router(question_banks_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(wrong_questions_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(practice_sessions_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(practice_records_student_router.router, dependencies=[Depends(get_current_user)])

