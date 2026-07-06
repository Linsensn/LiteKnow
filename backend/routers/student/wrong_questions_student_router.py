import logging
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from itertools import groupby

from config.database import get_db
from utils.deps import get_current_user
from services.wrong_question_service import wq_service
from crud import wrong_questions_crud
from utils.response import success

from schemas.common import ResponseModel, PageResult
from schemas.wrong_question_schemas import (
    WrongQuestionUpdate, WrongQuestionOut, BatchDeleteWrongQuestionsReq,
    WrongQuestionImport, BatchUpdateWrongQuestionsReq
)

audit_logger = logging.getLogger("liteknow.audit")
router = APIRouter(prefix="/wrong-questions", tags=["Student/Wrong Questions"])

@router.post("", response_model=ResponseModel[WrongQuestionOut])
async def create_single_wrong_question(
    data: WrongQuestionImport, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    obj_in = data.model_dump()
    result = await wrong_questions_crud.create_wrong_question(db=db, obj_in=obj_in, user_id=current_student.id)
    db.commit()
    audit_logger.info(f"Student {current_student.id} manually created wrong question {result.id}")
    return success(data=WrongQuestionOut.model_validate(result), message="错题新增成功")

@router.post("/bulk-import", response_model=ResponseModel[dict])
async def import_wrong_questions(
    data: List[WrongQuestionImport], db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    dict_data = [item.model_dump() for item in data]
    count = await wq_service.bulk_import_wrong_questions(db=db, user_id=current_student.id, questions_data=dict_data)
    audit_logger.info(f"Student {current_student.id} batch imported {count} wrong questions")
    return success(message=f"成功导入 {count} 道错题")

@router.get("/list", response_model=ResponseModel[PageResult[WrongQuestionOut]])
async def list_my_wrong_questions(
    keyword: str = Query(None, description="搜索错题内容", examples=["TSP遗传算法缺陷修复"]),
    sort_by: str = Query("desc", description="排序：asc或desc", examples=["desc"]),
    page: int = Query(1, ge=1, description="页码", examples=[1]),
    page_size: int = Query(20, ge=1, le=100, description="每页数量", examples=[20]),
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    result = await wq_service.get_my_wrong_questions(
        db=db, user_id=current_student.id, keyword=keyword, page=page, page_size=page_size, sort_by=sort_by
    )
    items_data = [WrongQuestionOut.model_validate(item) for item in result["items"]]
    
    page_data = PageResult(list=items_data, total=result["total"], page=page, page_size=page_size)
    return success(data=page_data, message="获取错题本成功")

@router.get("/tree", response_model=ResponseModel[List[dict]])
async def get_wrong_questions_tree(
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    items, _ = await wrong_questions_crud.get_multi_wrong_questions(db=db, user_id=current_student.id, limit=1000)
    list_data = [WrongQuestionOut.model_validate(i).model_dump() for i in items]
    
    for i in list_data:
        i["month_group"] = i["created_at"].strftime("%Y-%m") if i.get("created_at") else "未知时间"
        
    list_data.sort(key=lambda x: x["month_group"], reverse=True)
    tree_data = [
        {"month": key, "children": list(group)} 
        for key, group in groupby(list_data, key=lambda x: x["month_group"])
    ]
    return success(data=tree_data)

@router.get("/{wq_id}", response_model=ResponseModel[WrongQuestionOut])
async def get_wrong_question_detail(
    wq_id: int = Path(..., description="错题ID", examples=[9527]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    wq = await wq_service.get_wrong_question_detail(db=db, wq_id=wq_id, user_id=current_student.id)
    return success(data=WrongQuestionOut.model_validate(wq))

@router.put("/batch", response_model=ResponseModel[dict])
async def batch_update_wrong_questions(
    data: BatchUpdateWrongQuestionsReq, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    updated_count = await wrong_questions_crud.update_multi_wrong_questions(
        db=db, ids=data.ids, user_id=current_student.id, update_data=data.update_data.model_dump(exclude_unset=True)
    )
    db.commit()
    audit_logger.info(f"Student {current_student.id} batch updated wrong questions {data.ids}")
    return success(message=f"成功批量更新 {updated_count} 道错题")

@router.put("/{wq_id}", response_model=ResponseModel[dict])
async def update_single_wrong_question(
    data: WrongQuestionUpdate, wq_id: int = Path(..., description="错题ID", examples=[9527]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    updated_count = await wrong_questions_crud.update_wrong_question(
        db=db, id=wq_id, user_id=current_student.id, update_data=data.model_dump(exclude_unset=True)
    )
    db.commit()
    audit_logger.info(f"Student {current_student.id} updated wrong question {wq_id}")
    return success(message=f"错题更新成功，影响 {updated_count} 条")

@router.delete("/bulk", response_model=ResponseModel[dict])
async def remove_multi_wrong_questions(
    payload: BatchDeleteWrongQuestionsReq, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    deleted_count = await wq_service.bulk_remove_wrong_questions(db=db, wq_ids=payload.ids, user_id=current_student.id)
    audit_logger.warning(f"Student {current_student.id} batch removed wrong questions {payload.ids}")
    # 兼容若 Service 无返回值的情况
    return success(message=f"成功移出 {deleted_count or 0} 道错题")

@router.delete("/{wq_id}", response_model=ResponseModel[dict])
async def remove_wrong_question(
    wq_id: int = Path(..., description="错题ID", examples=[9527]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    deleted_count = await wq_service.remove_wrong_question(db=db, wq_id=wq_id, user_id=current_student.id)
    audit_logger.warning(f"Student {current_student.id} removed wrong question {wq_id}")
    return success(message=f"已成功移出 {deleted_count or 0} 道错题")

@router.get("/data/export")
async def export_wrong_questions(
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    csv_data = await wq_service.export_wrong_questions_to_csv(db=db, user_id=current_student.id)
    audit_logger.info(f"Student {current_student.id} exported wrong questions to CSV")
    return StreamingResponse(
        iter([csv_data.encode("utf-8-sig")]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=wrong_questions_{current_student.id}.csv"}
    )

@router.post("/data/import", response_model=ResponseModel[dict])
async def import_wrong_questions_csv(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    await wq_service.import_wrong_questions_from_csv(db=db, user_id=current_student.id, file=file)
    audit_logger.info(f"Student {current_student.id} imported wrong questions from {file.filename}")
    return success(message="错题数据导入完成")