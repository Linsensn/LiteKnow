# backend/routers/student/bank_question_student_router.py
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from services.bank_question_service import bq_service
from utils.response import success  
from schemas.bank_question_schema import QuestionResponse
router = APIRouter(prefix="/questions", tags=["Student/bank_question"])


@router.get("", summary="学生端分页浏览题库题目")
async def student_list_questions(
    bank_id: int = Query(..., description="必须指定题库ID"),
    difficulty: str = Query(None, description="按难度筛选"),
    keyword: str = Query(None, description="题干模糊搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    data = await bq_service.get_question_page(
        db=db, bank_id=bank_id, difficulty=difficulty, keyword=keyword,
        page=page, page_size=page_size
    )
    data.list = [QuestionResponse.model_validate(item) for item in data.list]
    return success(data=data)  


@router.get("/{question_id}", summary="查看单道题目详情")
async def student_get_question(
    question_id: int = Path(..., description="题目ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    data = await bq_service.get_question(db, question_id=question_id)
    return success(data=QuestionResponse.model_validate(data)) 