from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from services.question_bank_service import qb_service
from utils.response import success
from schemas.question_bank_schemas import QuestionBankCreate, QuestionBankOut, BulkDeleteIn

router = APIRouter(prefix="/question-banks", tags=["Student - Question Banks"])

@router.post("")
async def create_my_question_bank(
    data: QuestionBankCreate,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 创建属于自己的专属题库"""
    bank_in_dict = data.model_dump()
    result = await qb_service.create_bank(db=db, current_user=current_student, bank_in=bank_in_dict)
    return success(data=QuestionBankOut.model_validate(result).model_dump(), message="专属题库创建成功")

@router.get("")
async def list_my_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 仅查询当前学生创建的题库"""
    result = await qb_service.get_banks(db=db, current_user=current_student, keyword=keyword, page=page, page_size=page_size)
    items_data = [QuestionBankOut.model_validate(item).model_dump() for item in result["items"]]
    return success(data={"total": result["total"], "items": items_data}, message="获取题库列表成功")

@router.delete("/bulk")
async def student_bulk_delete_question_banks(
    data: BulkDeleteIn,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 批量删除自己名下的题库"""
    await qb_service.bulk_delete(db=db, current_user=current_student, bank_ids=data.bank_ids)
    return success(message="批量删除题库成功")