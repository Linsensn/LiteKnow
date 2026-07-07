import logging
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from itertools import groupby

from config.database import get_db
from utils.deps import get_current_user
from utils.response import success, fail
from utils.exceptions import ErrorCode

from schemas.common import ResponseModel, PageResult
from services.practice_record_service import pr_service
from crud import practice_records_crud
from schemas.practice_record_schemas import (
    PracticeRecordSubmit, PracticeRecordCreate, PracticeRecordUpdate,
    SubmitResultOut, PracticeRecordDetailOut, 
    BatchDeleteReq, BatchUpdateReq, StatusToggleReq
)

audit_logger = logging.getLogger("liteknow.audit")
router = APIRouter(prefix="/practice-records", tags=["Student/Practice Records"])

@router.post("/submit", response_model=ResponseModel[SubmitResultOut], summary="提交题目作答")
async def submit_question_answer(
    data: PracticeRecordSubmit, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    # 修改：新增传入 option_sequence 字段
    result = await pr_service.submit_answer(
        db=db, 
        user_id=current_student.id, 
        session_id=data.session_id, 
        question_id=data.question_id, 
        user_answer=data.user_answer, 
        correct_answer=data.correct_answer, 
        question_content=data.question_content, 
        current_index=data.current_index,
        option_sequence=data.option_sequence
    )
    audit_logger.info(f"User {current_student.id} submitted question {data.question_id}")
    return success(data=SubmitResultOut(is_correct=result["is_correct"]), message="答题记录提交成功")

@router.post("", response_model=ResponseModel[PracticeRecordDetailOut], summary="新增答题记录")
async def create_record(
    data: PracticeRecordCreate, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    obj_in = data.model_dump()
    obj_in["user_id"] = current_student.id
    record = await practice_records_crud.create_practice_record(db=db, obj_in=obj_in)
    db.commit()
    audit_logger.info(f"User {current_student.id} manually created record {record.id}")
    return success(data=PracticeRecordDetailOut.model_validate(record))

@router.post("/batch", response_model=ResponseModel[dict], summary="批量新增答题记录")
async def create_batch_records(
    data: List[PracticeRecordCreate], db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    objs_in = [{"user_id": current_student.id, **item.model_dump()} for item in data]
    await practice_records_crud.create_multi_records(db=db, objs_in=objs_in)
    db.commit()
    audit_logger.info(f"User {current_student.id} batch created {len(objs_in)} records")
    return success(message=f"批量新增 {len(objs_in)} 条成功")

@router.get("/list", response_model=ResponseModel[PageResult[PracticeRecordDetailOut]], summary="获取答题记录列表")
async def get_practice_records_list(
    session_id: Optional[int] = Query(None, description="多条件：按练习会话过滤", examples=[1024]),
    is_correct: Optional[bool] = Query(None, description="多条件：按正误状态过滤", examples=[True]),
    sort_by: str = Query("desc", description="排序与聚合：asc或desc", examples=["desc"]),
    skip: int = Query(0, description="分页：起始偏移量", examples=[0]),
    limit: int = Query(20, le=100, description="分页：每页返回数量", examples=[20]),
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    records, total = await practice_records_crud.get_multi_records(
        db=db, user_id=current_student.id, session_id=session_id, 
        is_correct=is_correct, skip=skip, limit=limit, sort_by=sort_by
    )
    list_data = [PracticeRecordDetailOut.model_validate(r) for r in records]
    
    page_data = PageResult(list=list_data, total=total, page=(skip // limit) + 1, page_size=limit)
    return success(data=page_data)

@router.get("/tree", response_model=ResponseModel[List[dict]], summary="获取按会话分组的答题记录树")
async def get_practice_records_tree(
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    records, _ = await practice_records_crud.get_multi_records(db=db, user_id=current_student.id, limit=1000)
    list_data = [PracticeRecordDetailOut.model_validate(r).model_dump() for r in records]
    
    list_data.sort(key=lambda x: x["session_id"])
    tree_data = [
        {"session_id": key, "children": list(group)} 
        for key, group in groupby(list_data, key=lambda x: x["session_id"])
    ]
    return success(data=tree_data)

@router.get("/{record_id}", response_model=ResponseModel[PracticeRecordDetailOut], summary="获取单条答题记录详情")
async def get_practice_record_detail(
    record_id: int = Path(..., description="主键ID", examples=[1001]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    record = await practice_records_crud.get_practice_record(db=db, id=record_id)
    if not record or record.user_id != current_student.id:
        return fail(code=ErrorCode.DATA_NOT_FOUND, message="记录不存在或无权访问")
    return success(data=PracticeRecordDetailOut.model_validate(record))

@router.put("/batch", response_model=ResponseModel[dict], summary="批量修改答题记录")
async def update_batch_records(
    data: BatchUpdateReq, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    updated_count = await practice_records_crud.update_multi_records(db=db, ids=data.ids, obj_in=data.update_data.model_dump(exclude_unset=True))
    db.commit()
    audit_logger.info(f"User {current_student.id} batch updated records {data.ids}")
    return success(message=f"成功更新 {updated_count} 条记录")

@router.put("/{record_id}", response_model=ResponseModel[dict], summary="修改单条答题记录")
async def update_single_record(
    data: PracticeRecordUpdate, record_id: int = Path(..., description="主键ID", examples=[1001]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    updated_count = await practice_records_crud.update_record(db=db, id=record_id, obj_in=data.model_dump(exclude_unset=True))
    db.commit()
    audit_logger.info(f"User {current_student.id} updated record {record_id}")
    return success(message=f"记录更新成功，影响 {updated_count} 条")

@router.patch("/{record_id}/status", response_model=ResponseModel[dict], summary="切换答题记录正误状态")
async def toggle_record_status(
    payload: StatusToggleReq, record_id: int = Path(..., description="主键ID", examples=[1001]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    updated_count = await practice_records_crud.toggle_record_status(db=db, id=record_id, is_correct=payload.is_correct)
    db.commit() 
    audit_logger.info(f"User {current_student.id} toggled status for record {record_id} to {payload.is_correct}")
    return success(message=f"状态更新成功，影响 {updated_count} 条")

@router.delete("/batch", response_model=ResponseModel[dict], summary="批量删除答题记录")
async def delete_batch_records(
    payload: BatchDeleteReq, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    deleted_count = await practice_records_crud.delete_records_by_ids(db=db, ids=payload.ids)
    db.commit()
    audit_logger.warning(f"User {current_student.id} batch deleted {deleted_count} records")
    return success(message=f"成功删除 {deleted_count} 条记录")

@router.delete("/{record_id}", response_model=ResponseModel[dict], summary="删除单条答题记录")
async def delete_single_record(
    record_id: int = Path(..., description="主键ID", examples=[1001]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    deleted_count = await practice_records_crud.delete_records_by_ids(db=db, ids=[record_id])
    db.commit()
    audit_logger.warning(f"User {current_student.id} deleted record {record_id}")
    return success(message=f"成功删除 {deleted_count} 条记录")

@router.get("/session/{session_id}/stats", response_model=ResponseModel[dict], summary="获取会话答题统计")
async def get_session_stats(
    session_id: int = Path(..., description="会话ID", examples=[1024]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    stats = await pr_service.get_session_analysis(db=db, session_id=session_id)
    return success(data=stats)

@router.get("/export/csv", summary="导出答题记录为CSV")
async def export_records(
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    csv_data = await pr_service.export_user_records_to_csv(db=db, user_id=current_student.id)
    audit_logger.info(f"User {current_student.id} exported practice records")
    return StreamingResponse(
        iter([csv_data.encode("utf-8-sig")]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=practice_records_{current_student.id}.csv"}
    )

@router.post("/import/csv", response_model=ResponseModel[dict], summary="从CSV导入答题记录")
async def import_records(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    await pr_service.import_user_records_from_csv(db=db, user_id=current_student.id, file=file)
    audit_logger.info(f"User {current_student.id} imported records from {file.filename}")
    return success(message="数据导入完成")