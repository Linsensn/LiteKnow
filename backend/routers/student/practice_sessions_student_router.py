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
from services.practice_session_service import ps_service
from crud import practice_sessions_crud
from schemas.practice_session_schemas import (
    PracticeSessionCreate, PracticeSessionUpdate, PracticeSessionOut, 
    PracticeSessionDetailOut, BatchDeleteSessionReq, BatchUpdateSessionReq, StatusToggleReq
)

audit_logger = logging.getLogger("liteknow.audit")
router = APIRouter(prefix="/practice-sessions", tags=["Student/Practice Sessions"])

@router.post("", response_model=ResponseModel[PracticeSessionOut], summary="发起新的练习会话")
async def start_practice_session(
    data: PracticeSessionCreate, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[业务] 发起一次新的练习会话，并生成题号序列"""
    result = await ps_service.start_new_session(
        db=db, user_id=current_student.id, bank_id=data.bank_id, 
        mode=data.practice_mode, is_options_shuffled=data.is_options_shuffled, 
        question_sequence=data.question_sequence
    )
    audit_logger.info(f"User {current_student.id} started new session {result.id}")
    return success(data=PracticeSessionOut.model_validate(result), message="练习会话创建成功")

@router.post("/batch", response_model=ResponseModel[dict], summary="批量创建练习会话")
async def create_batch_sessions(
    data: List[PracticeSessionCreate], db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[基础] 批量创建练习会话"""
    objs_in = [{"user_id": current_student.id, "last_viewed_index": 0, "status": "ongoing", **item.model_dump()} for item in data]
    await practice_sessions_crud.create_multi_sessions(db=db, objs_in=objs_in)
    db.commit()
    audit_logger.info(f"User {current_student.id} batch created {len(objs_in)} sessions")
    return success(message=f"批量新增 {len(objs_in)} 条成功")

@router.get("/list", response_model=ResponseModel[PageResult[PracticeSessionDetailOut]], summary="分页获取会话列表")
async def get_sessions_list(
    status: Optional[str] = Query(None, description="按状态过滤：ongoing, completed", examples=["ongoing"]),
    keyword: Optional[str] = Query(None, description="模糊搜索：练习模式", examples=["STM32固件开发测试"]),
    sort_by: str = Query("desc", description="排序：asc或desc", examples=["desc"]),
    skip: int = Query(0, description="分页起始偏移量", examples=[0]),
    limit: int = Query(20, le=100, description="每页返回数量，最大100", examples=[20]),
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[查询] 关联题库分页获取会话列表，严格使用 PageResult"""
    sessions, total = await practice_sessions_crud.get_multi_sessions(
        db=db, user_id=current_student.id, status=status, search_keyword=keyword, 
        skip=skip, limit=limit, sort_by=sort_by
    )
    
    list_data = []
    for item in sessions:
        dump_data = PracticeSessionOut.model_validate(item).model_dump()
        dump_data["bank_name"] = item.bank.bank_name if hasattr(item, 'bank') and item.bank else "未知题库"
        list_data.append(PracticeSessionDetailOut(**dump_data))
        
    page_data = PageResult(list=list_data, total=total, page=(skip // limit) + 1, page_size=limit)
    return success(data=page_data)

@router.get("/tree", response_model=ResponseModel[List[dict]], summary="获取按状态分组的会话树")
async def get_practice_sessions_tree(
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[查询] 树形查询：将历史会话按 ongoing/completed 状态进行分组"""
    sessions, _ = await practice_sessions_crud.get_multi_sessions(db=db, user_id=current_student.id, limit=1000)
    list_data = [PracticeSessionOut.model_validate(s).model_dump() for s in sessions]
    
    list_data.sort(key=lambda x: str(x.get("status")))
    tree_data = [
        {"status_group": key, "children": list(group)} 
        for key, group in groupby(list_data, key=lambda x: str(x.get("status")))
    ]
    return success(data=tree_data)

@router.get("/{session_id}", response_model=ResponseModel[PracticeSessionOut], summary="获取单条会话进度详情")
async def get_practice_session_progress(
    session_id: int = Path(..., description="会话ID", examples=[2048]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[查询] 恢复中断的进度，查看单条会话信息"""
    result = await ps_service.get_session_detail(db=db, session_id=session_id, user_id=current_student.id)
    return success(data=PracticeSessionOut.model_validate(result))

@router.put("/batch", response_model=ResponseModel[dict], summary="批量修改练习会话")
async def update_batch_sessions(
    data: BatchUpdateSessionReq, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[基础] 批量修改会话"""
    updated_count = await practice_sessions_crud.update_multi_sessions(db=db, ids=data.ids, obj_in=data.update_data.model_dump(exclude_unset=True))
    db.commit()
    audit_logger.info(f"User {current_student.id} batch updated sessions {data.ids}")
    return success(message=f"成功更新 {updated_count} 条会话")

@router.put("/{session_id}", response_model=ResponseModel[dict], summary="修改单条练习会话")
async def update_single_session(
    data: PracticeSessionUpdate, session_id: int = Path(..., description="会话ID", examples=[2048]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[基础] 修改单条会话信息"""
    updated_count = await practice_sessions_crud.update_session(db=db, id=session_id, obj_in=data.model_dump(exclude_unset=True))
    db.commit()
    audit_logger.info(f"User {current_student.id} updated session {session_id}")
    return success(message=f"会话更新成功，影响 {updated_count} 条")

@router.patch("/{session_id}/status", response_model=ResponseModel[dict], summary="强制结束会话/主动交卷")
async def submit_practice_session(
    payload: StatusToggleReq, session_id: int = Path(..., description="会话ID", examples=[2048]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[业务] 强制结束会话/主动交卷"""
    await practice_sessions_crud.update_session_progress(db=db, session_id=session_id, last_viewed_index=0, status=payload.status)
    db.commit()
    audit_logger.info(f"User {current_student.id} toggled status of session {session_id} to {payload.status}")
    return success(message=f"状态已更新为 {payload.status}")

@router.delete("/batch", response_model=ResponseModel[dict], summary="批量删除练习会话")
async def delete_batch_sessions(
    payload: BatchDeleteSessionReq, db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[基础] 批量删除记录"""
    deleted_count = await practice_sessions_crud.delete_sessions_by_ids(db=db, ids=payload.ids)
    db.commit()
    audit_logger.warning(f"User {current_student.id} batch deleted {deleted_count} sessions")
    return success(message=f"成功删除 {deleted_count} 条会话")

@router.delete("/{session_id}", response_model=ResponseModel[dict], summary="删除单条练习会话")
async def delete_single_session(
    session_id: int = Path(..., description="会话ID", examples=[2048]), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[基础] 删除单条记录"""
    deleted_count = await practice_sessions_crud.delete_sessions_by_ids(db=db, ids=[session_id])
    db.commit()
    audit_logger.warning(f"User {current_student.id} deleted session {session_id}")
    return success(message=f"成功删除 {deleted_count} 条会话")

@router.get("/export/csv", summary="导出历史会话为CSV")
async def export_sessions(
    db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[业务] 导出历史会话数据为 CSV"""
    csv_data = await ps_service.export_sessions_to_csv(db=db, user_id=current_student.id)
    audit_logger.info(f"User {current_student.id} exported practice sessions")
    return StreamingResponse(
        iter([csv_data.encode("utf-8-sig")]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=practice_sessions_{current_student.id}.csv"}
    )

@router.post("/import/csv", response_model=ResponseModel[dict], summary="从CSV导入历史会话")
async def import_sessions(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_student: dict = Depends(get_current_user)
):
    """[业务] 从 CSV 导入历史会话"""
    await ps_service.import_sessions_from_csv(db=db, user_id=current_student.id, file=file)
    audit_logger.info(f"User {current_student.id} imported sessions from {file.filename}")
    return success(message="数据导入完成")