from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from services.wrong_question_service import wq_service
from utils.response import success
from schemas.wrong_question_schemas import WrongQuestionUpdateAnalysis, WrongQuestionOut

router = APIRouter(prefix="/wrong-questions", tags=["Student - Wrong Questions"])

@router.get("")
async def list_my_wrong_questions(
    keyword: str = Query(None, description="搜索错题内容"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 分页获取我的错题本记录"""
    result = await wq_service.get_my_wrong_questions(
        db=db, user_id=current_student["id"], keyword=keyword, page=page, page_size=page_size
    )
    items_data = [WrongQuestionOut.model_validate(item).model_dump() for item in result["items"]]
    return success(data={"total": result["total"], "items": items_data}, message="获取错题本成功")

@router.put("/{wq_id}/analysis")
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

@router.delete("/{wq_id}")
async def remove_wrong_question(
    wq_id: int = Path(..., description="错题ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 掌握该错题后，将其从错题本中移除"""
    await wq_service.remove_wrong_question(db=db, wq_id=wq_id, user_id=current_student["id"])
    return success(message="已成功移出错题本")