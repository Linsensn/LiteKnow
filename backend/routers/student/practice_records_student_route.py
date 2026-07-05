from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from services.practice_record_service import pr_service
from utils.response import success

router = APIRouter(prefix="/practice-records", tags=["Student - Practice Records"])

@router.post("/submit")
async def submit_question_answer(
    session_id: int = Body(..., description="当前关联的练习会话ID"),
    question_id: int = Body(..., description="答题的题目ID"),
    user_answer: str = Body(..., description="用户的选项或文本回答"),
    correct_answer: str = Body(..., description="正确答案比对标识"),
    question_content: str = Body(..., description="题干快照，用于错题本冗余展示"),
    current_index: int = Body(..., description="该题目在序列中的位置索引，用于记录进度"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    [学生端] 提交单道题的作答。
    包含逻辑：记录答题历史 -> 自动判题 -> 若答错自动归档至个人错题本 -> 更新会话 last_viewed_index
    """
    result = await pr_service.submit_answer(
        db=db, 
        user_id=current_student["id"], 
        session_id=session_id, 
        question_id=question_id, 
        user_answer=user_answer, 
        correct_answer=correct_answer, 
        question_content=question_content, 
        current_index=current_index
    )
    # 使用 success 封装返回信息
    return success(data=result, message="答题记录提交成功")