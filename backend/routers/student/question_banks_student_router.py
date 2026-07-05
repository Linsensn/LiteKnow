import logging
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from itertools import groupby

from config.database import get_db
from utils.deps import get_current_user
from services.question_bank_service import qb_service
from crud import question_banks_crud
from utils.response import success

# 引入 User 模型作为正确的类型提示
from models.users import User
from schemas.common import ResponseModel, PageResult
from schemas.question_bank_schemas import (
    QuestionBankCreate, QuestionBankUpdate, QuestionBankOut, 
    BulkDeleteIn, BatchUpdateBankReq
)

audit_logger = logging.getLogger("liteknow.audit")
router = APIRouter(prefix="/question-banks", tags=["Student - Question Banks"])

@router.post("", response_model=ResponseModel[QuestionBankOut])
async def create_my_question_bank(
    data: QuestionBankCreate, db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    result = await qb_service.create_bank(db=db, current_user=current_student, bank_in=data.model_dump())
    audit_logger.info(f"Student {current_student.id} created bank {result.id}")
    return success(data=QuestionBankOut.model_validate(result), message="题库创建成功")

@router.post("/batch", response_model=ResponseModel[dict])
async def create_batch_question_banks(
    data: List[QuestionBankCreate], db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    objs_in = [item.model_dump() for item in data]
    await question_banks_crud.create_multi_question_banks(db=db, objs_in=objs_in, user_id=current_student.id)
    db.commit()
    audit_logger.info(f"Student {current_student.id} batch created {len(objs_in)} banks")
    return success(message=f"成功批量创建 {len(objs_in)} 个题库")

@router.get("", response_model=ResponseModel[PageResult[QuestionBankOut]])
async def list_my_question_banks(
    keyword: str = Query(None, description="模糊搜索题库名或描述"),
    sort_by: str = Query("desc", description="排序：asc或desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    result = await qb_service.get_banks(db=db, current_user=current_student, keyword=keyword, page=page, page_size=page_size, sort_by=sort_by)
    items_data = [QuestionBankOut.model_validate(item) for item in result["items"]]
    
    page_data = PageResult(
        list=items_data, 
        total=result["total"], 
        page=page, 
        page_size=page_size
    )
    return success(data=page_data, message="获取题库列表成功")

@router.get("/tree", response_model=ResponseModel[List[dict]])
async def get_banks_tree(
    db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    banks, _ = await question_banks_crud.get_multi_question_banks(db=db, user_id=current_student.id, limit=1000)
    list_data = [QuestionBankOut.model_validate(b).model_dump() for b in banks]
    
    for b in list_data:
        b["month_group"] = b["created_at"].strftime("%Y-%m") if b.get("created_at") else "未知时间"
        
    list_data.sort(key=lambda x: x["month_group"], reverse=True)
    tree_data = [
        {"month": key, "children": list(group)} 
        for key, group in groupby(list_data, key=lambda x: x["month_group"])
    ]
    return success(data=tree_data)

@router.get("/{bank_id}", response_model=ResponseModel[QuestionBankOut])
async def get_my_question_bank_detail(
    bank_id: int = Path(...), db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    bank = await qb_service.get_bank_detail(db=db, current_user=current_student, bank_id=bank_id)
    return success(data=QuestionBankOut.model_validate(bank))

@router.put("/{bank_id}", response_model=ResponseModel[dict])
async def update_my_question_bank(
    data: QuestionBankUpdate, bank_id: int = Path(...), db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    await qb_service.update_bank(db=db, current_user=current_student, bank_id=bank_id, update_data=data.model_dump())
    audit_logger.info(f"Student {current_student.id} updated bank {bank_id}")
    return success(message="题库信息更新成功")

@router.put("/batch/update", response_model=ResponseModel[dict])
async def batch_update_my_banks(
    data: BatchUpdateBankReq, db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    await question_banks_crud.update_multi_banks(db=db, ids=data.ids, update_data=data.update_data.model_dump(exclude_unset=True), user_id=current_student.id)
    db.commit()
    audit_logger.info(f"Student {current_student.id} batch updated banks {data.ids}")
    return success(message=f"成功更新 {len(data.ids)} 个题库")

@router.delete("/bulk", response_model=ResponseModel[dict])
async def student_bulk_delete_question_banks(
    data: BulkDeleteIn, db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    await qb_service.bulk_delete(db=db, current_user=current_student, bank_ids=data.bank_ids)
    audit_logger.warning(f"Student {current_student.id} batch deleted banks {data.bank_ids}")
    return success(message=f"成功批量删除 {len(data.bank_ids)} 个题库")

@router.delete("/{bank_id}", response_model=ResponseModel[dict])
async def student_delete_single_bank(
    bank_id: int = Path(...), db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    await qb_service.bulk_delete(db=db, current_user=current_student, bank_ids=[bank_id])
    audit_logger.warning(f"Student {current_student.id} deleted bank {bank_id}")
    return success(message="题库删除成功")

@router.get("/data/export")
async def export_my_banks(
    db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    csv_data = await qb_service.export_banks_to_csv(db=db, current_user=current_student)
    audit_logger.info(f"Student {current_student.id} exported banks to CSV")
    return StreamingResponse(
        iter([csv_data.encode("utf-8-sig")]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=my_question_banks_{current_student.id}.csv"}
    )

@router.post("/data/import", response_model=ResponseModel[dict])
async def import_my_banks(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_student: User = Depends(get_current_user)
):
    await qb_service.import_banks_from_csv(db=db, current_user=current_student, file=file)
    audit_logger.info(f"Student {current_student.id} imported banks from {file.filename}")
    return success(message="题库导入完成")