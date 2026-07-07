r"""
@Desc    : 微信小程序学生端模块路由初始化
"""

from fastapi import APIRouter, Depends
from utils.deps import get_current_user, get_admin_user
student_router = APIRouter()

# 1. 在这里导入 ai_bank_router
from . import (
    ai_summary_router,
    ai_bank_router,           # <-- 新增这一行：导入你的智能测验/题库路由
    practice_records_student_router,
    practice_sessions_student_router,
    question_banks_student_router,
    student_student_router, 
    sessions_student_router, 
    bank_question_student_router,
    favorite_student_router,
    attachment_student_router,
    message_student_router, 
    wrong_questions_student_router
)

# 挂载学生视角的学习与练习路由，同步修改名称
student_router.include_router(student_student_router.router)
student_router.include_router(sessions_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(bank_question_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(favorite_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(attachment_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(message_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(question_banks_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(wrong_questions_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(practice_sessions_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(practice_records_student_router.router, dependencies=[Depends(get_current_user)])
student_router.include_router(ai_summary_router.router, dependencies=[Depends(get_current_user)])

# 2. 在这里挂载 ai_bank_router
student_router.include_router(ai_bank_router.router, dependencies=[Depends(get_current_user)]) # <-- 新增这一行：挂载你的路由
