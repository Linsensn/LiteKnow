from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_current_user
from services.question_bank_service import qb_service
from utils.response import success
from schemas.question_bank_schemas import (
    QuestionBankCreate, 
    QuestionBankUpdate,
    QuestionBankOut, 
    BulkDeleteIn
)

router = APIRouter(prefix="/question-banks", tags=["Student - Question Banks"])

@router.post("")
async def create_my_question_bank(
    data: QuestionBankCreate,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 创建专属题库"""
    result = await qb_service.create_bank(db=db, current_user=current_student, bank_in=data.model_dump())
    return success(data=QuestionBankOut.model_validate(result).model_dump(), message="题库创建成功")

@router.get("")
async def list_my_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 分页获取我的题库列表"""
    result = await qb_service.get_banks(db=db, current_user=current_student, keyword=keyword, page=page, page_size=page_size)
    items_data = [QuestionBankOut.model_validate(item).model_dump() for item in result["items"]]
    return success(data={"total": result["total"], "items": items_data}, message="获取题库列表成功")

@router.get("/{bank_id}")
async def get_my_question_bank_detail(
    bank_id: int = Path(..., description="题库ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 获取某个特定题库详情"""
    bank = await qb_service.get_bank_detail(db=db, current_user=current_student, bank_id=bank_id)
    return success(data=QuestionBankOut.model_validate(bank).model_dump())

@router.patch("/{bank_id}")
async def update_my_question_bank(
    data: QuestionBankUpdate,
    bank_id: int = Path(..., description="题库ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 修改自己名下题库的信息（名称或描述）"""
    await qb_service.update_bank(db=db, current_user=current_student, bank_id=bank_id, update_data=data.model_dump())
    return success(message="题库信息更新成功")

@router.delete("/bulk")
async def student_bulk_delete_question_banks(
    data: BulkDeleteIn,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 批量删除题库"""
    await qb_service.bulk_delete(db=db, current_user=current_student, bank_ids=data.bank_ids)
    return success(message=f"成功批量删除 {len(data.bank_ids)} 个题库")

@router.delete("/{bank_id}")
async def student_delete_single_bank(
    bank_id: int = Path(..., description="题库ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 单条删除题库"""
    await qb_service.bulk_delete(db=db, current_user=current_student, bank_ids=[bank_id])
    return success(message="题库删除成功")