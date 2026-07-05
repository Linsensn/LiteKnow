from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.database import get_db
from utils.deps import get_current_user
from services.wrong_question_service import wq_service
from utils.response import success
from schemas.wrong_question_schemas import (
    WrongQuestionUpdateAnalysis, 
    WrongQuestionOut, 
    BatchDeleteWrongQuestionsReq,
    WrongQuestionImport
)

router = APIRouter(prefix="/wrong-questions", tags=["Student - Wrong Questions"])

@router.get("", response_model=dict)
async def list_my_wrong_questions(
    keyword: str = Query(None, description="搜索错题内容"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 分页获取我的错题本记录"""
    result = await wq_service.get_my_wrong_questions(
        db=db, user_id=current_student["id"], keyword=keyword, page=page, page_size=page_size
    )
    items_data = [WrongQuestionOut.model_validate(item).model_dump() for item in result["items"]]
    return success(data={"total": result["total"], "items": items_data}, message="获取错题本成功")

@router.get("/{wq_id}", response_model=dict)
async def get_wrong_question_detail(
    wq_id: int = Path(..., description="错题ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 获取单道错题的具体详情"""
    wq = await wq_service.get_wrong_question_detail(db=db, wq_id=wq_id, user_id=current_student["id"])
    return success(data=WrongQuestionOut.model_validate(wq).model_dump())

@router.post("/bulk-import", response_model=dict)
async def import_wrong_questions(
    data: List[WrongQuestionImport],
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 批量手动/外部导入错题"""
    dict_data = [item.model_dump() for item in data]
    count = await wq_service.bulk_import_wrong_questions(db=db, user_id=current_student["id"], questions_data=dict_data)
    return success(message=f"成功导入 {count} 道错题")

@router.patch("/{wq_id}/analysis", response_model=dict)
async def supplement_my_analysis(
    data: WrongQuestionUpdateAnalysis,
    wq_id: int = Path(..., description="错题ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 为某道错题补充个人的解析体会"""
    await wq_service.update_my_analysis(
        db=db, wq_id=wq_id, user_id=current_student["id"], my_analysis=data.my_analysis
    )
    return success(message="个人解析已保存")

@router.delete("/bulk", response_model=dict)
async def remove_multi_wrong_questions(
    payload: BatchDeleteWrongQuestionsReq,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 批量移出已掌握的错题"""
    await wq_service.bulk_remove_wrong_questions(db=db, wq_ids=payload.ids, user_id=current_student["id"])
    return success(message=f"成功移出 {len(payload.ids)} 道错题")

@router.delete("/{wq_id}", response_model=dict)
async def remove_wrong_question(
    wq_id: int = Path(..., description="错题ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 掌握该错题后，将其从错题本中移除"""
    await wq_service.remove_wrong_question(db=db, wq_id=wq_id, user_id=current_student["id"])
    return success(message="已成功移出错题本")