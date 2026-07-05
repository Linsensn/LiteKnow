from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from services.practice_record_service import pr_service
from utils.response import success
from schemas.practice_record_schemas import PracticeRecordSubmit, SubmitResultOut

router = APIRouter(prefix="/practice-records", tags=["Student - Practice Records"])

@router.post("/submit")
async def submit_question_answer(
    data: PracticeRecordSubmit,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 提交单道题的作答"""
    result = await pr_service.submit_answer(
        db=db, 
        user_id=current_student["id"], 
        session_id=data.session_id, 
        question_id=data.question_id, 
        user_answer=data.user_answer, 
        correct_answer=data.correct_answer, 
        question_content=data.question_content, 
        current_index=data.current_index
    )
    # 结果封装输出 Schema
    out_data = SubmitResultOut(is_correct=result["is_correct"])
    return success(data=out_data.model_dump(), message="答题记录提交成功")