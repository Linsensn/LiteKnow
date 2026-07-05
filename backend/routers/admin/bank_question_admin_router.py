# backend/routers/admin/bank_questions_admin_route.py
from fastapi import APIRouter, Depends, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.database import get_db
from utils.deps import get_admin_user
from services.bank_question_service import bq_service
from schemas.bank_question_schema import QuestionCreate, QuestionUpdate

router = APIRouter(prefix="/questions", tags=["Admin - 题目管理"])


@router.get("", summary="分页查询题目列表")
async def admin_list_questions(
    bank_id: int = Query(None, description="按题库ID筛选"),
    difficulty: str = Query(None, description="按难度筛选: easy/medium/hard"),
    keyword: str = Query(None, description="题干模糊搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    return await bq_service.get_question_page(
        db=db, bank_id=bank_id, difficulty=difficulty, keyword=keyword,
        page=page, page_size=page_size
    )


@router.get("/{question_id}", summary="查询单条题目详情")
async def admin_get_question(
    question_id: int = Path(..., description="题目ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    return await bq_service.get_question(db, question_id=question_id)


@router.post("", summary="单条录入题目")
async def admin_create_question(
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    return await bq_service.create_question(db, obj_in=question_in)


@router.post("/batch", summary="批量导入题目")
async def admin_create_questions_batch(
    questions_in: List[QuestionCreate] = Body(..., description="题目列表"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    count = await bq_service.create_question_batch(db, objects_in=questions_in)
    return {"imported_count": count}


@router.put("/{question_id}", summary="修改题目信息")
async def admin_update_question(
    question_id: int = Path(..., description="题目ID"),
    question_in: QuestionUpdate = Body(..., description="更新内容"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    return await bq_service.update_question(db, question_id=question_id, obj_in=question_in)


@router.delete("/{question_id}", summary="逻辑删除题目")
async def admin_delete_question(
    question_id: int = Path(..., description="题目ID"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    await bq_service.delete_question(db, question_id=question_id)
    return {"message": "删除成功"}