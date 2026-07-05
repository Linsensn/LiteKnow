from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from config.database import get_db
from utils.deps import get_current_user
from services.practice_record_service import pr_service
from crud import practice_records_crud
from utils.response import success
from schemas.practice_record_schemas import (
    PracticeRecordSubmit, 
    SubmitResultOut,
    PracticeRecordDetailOut, 
    BatchDeleteReq, 
    StatusToggleReq
)

router = APIRouter(prefix="/practice-records", tags=["Student - Practice Records"])

@router.post("/submit")
async def submit_question_answer(
    data: PracticeRecordSubmit,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 提交单道题的作答"""
    result = await pr_service.submit_answer(
        db=db, 
        user_id=current_student["id"], 
        session_id=data.session_id, 
        question_id=data.question_id, 
        user_answer=data.user_answer, 
        correct_answer=data.correct_answer, 
        question_content=data.question_content, 
        current_index=data.current_index
    )
    out_data = SubmitResultOut(is_correct=result["is_correct"])
    return success(data=out_data.model_dump(), message="答题记录提交成功")

@router.get("/list", response_model=dict)
async def get_practice_records_list(
    session_id: Optional[int] = Query(None, description="按练习会话过滤"),
    skip: int = Query(0, description="分页起始偏移量"),
    limit: int = Query(20, le=100, description="每页返回数量，最大100"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 分页获取我的历史答题记录，支持按 session_id 过滤"""
    records = await practice_records_crud.get_multi_records(
        db=db, 
        user_id=current_student["id"], 
        session_id=session_id, 
        skip=skip, 
        limit=limit
    )
    data = [PracticeRecordDetailOut.model_validate(r).model_dump() for r in records]
    return success(data={"items": data, "total_in_page": len(data)})

@router.get("/{record_id}", response_model=dict)
async def get_practice_record_detail(
    record_id: int = Path(..., description="答题记录的主键ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 获取某一条答题记录的详细信息"""
    record = await practice_records_crud.get_practice_record(db=db, id=record_id)
    
    if not record or record.user_id != current_student["id"]:
        return success(code=404, message="记录不存在或无权访问", data=None)
        
    return success(data=PracticeRecordDetailOut.model_validate(record).model_dump())

@router.get("/session/{session_id}/stats")
async def get_session_stats(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 获取单次练习的统计聚合数据（正确率、完成度）"""
    stats = await pr_service.get_session_analysis(db=db, session_id=session_id)
    return success(data=stats)

@router.get("/export/csv")
async def export_records(
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 数据导出：下载历史答题记录 (CSV)"""
    csv_data = await pr_service.export_user_records_to_csv(db=db, user_id=current_student["id"])
    
    iterfile = iter([csv_data.encode("utf-8-sig")]) 
    return StreamingResponse(
        iterfile,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=practice_records_{current_student['id']}.csv"}
    )

@router.patch("/{record_id}/status", response_model=dict)
async def toggle_record_status(
    payload: StatusToggleReq,
    record_id: int = Path(..., description="答题记录的主键ID"),
    db: AsyncSession = Depends(get_db),
):
    """[教师/管理端] 切换某条记录的正误状态"""
    await practice_records_crud.toggle_record_status(
        db=db, 
        id=record_id, 
        is_correct=payload.is_correct
    )
    await db.commit() 
    return success(message="状态更新成功")

@router.delete("/", response_model=dict)
async def delete_practice_records(
    payload: BatchDeleteReq,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 批量或单条删除答题记录 (传单个ID即为单条删除)"""
    await practice_records_crud.delete_records_by_ids(db=db, ids=payload.ids)
    await db.commit()
    return success(message=f"成功删除 {len(payload.ids)} 条记录")