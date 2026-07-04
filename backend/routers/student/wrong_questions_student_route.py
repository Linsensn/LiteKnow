from fastapi import APIRouter, Depends, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.auth import get_current_student
from services.wrong_question_service import wq_service

router = APIRouter(prefix="/wrong-questions", tags=["Student - Wrong Questions"])

@router.get("")
async def list_my_wrong_questions(
    keyword: str = Query(None, description="搜索错题内容"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_student)
):
    """
    [学生端] 分页获取我的错题本记录
    """
    return await wq_service.get_my_wrong_questions(
        db=db, user_id=current_student["id"], keyword=keyword, page=page, page_size=page_size
    )

@router.put("/{wq_id}/analysis")
async def supplement_my_analysis(
    wq_id: int = Path(..., description="错题ID"),
    my_analysis: str = Body(..., embed=True, description="学生自己撰写的反思与解析"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_student)
):
    """
    [学生端] 为某道错题补充个人的解析体会
    """
    await wq_service.update_my_analysis(
        db=db, wq_id=wq_id, user_id=current_student["id"], my_analysis=my_analysis
    )
    return {"message": "个人解析已保存"}

@router.delete("/{wq_id}")
async def remove_wrong_question(
    wq_id: int = Path(..., description="错题ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_student)
):
    """
    [学生端] 掌握该错题后，将其从错题本中移除
    """
    await wq_service.remove_wrong_question(db=db, wq_id=wq_id, user_id=current_student["id"])
    return {"message": "已成功移出错题本"}