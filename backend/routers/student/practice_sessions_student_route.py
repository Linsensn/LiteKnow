from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from config.database import get_db
from utils.deps import get_current_user
from services.practice_session_service import ps_service
from utils.response import success
from schemas.practice_session_schemas import (
    PracticeSessionCreate, 
    PracticeSessionOut, 
    PracticeSessionDetailOut,
    BatchDeleteSessionReq
)

router = APIRouter(prefix="/practice-sessions", tags=["Student - Practice Sessions"])

@router.post("")
async def start_practice_session(
    data: PracticeSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 发起一次新的练习会话"""
    result = await ps_service.start_new_session(
        db=db, 
        user_id=current_student["id"], 
        bank_id=data.bank_id, 
        mode=data.mode, 
        question_ids=data.question_ids
    )
    return success(data=PracticeSessionOut.model_validate(result).model_dump(), message="练习会话创建成功")

@router.get("/list", response_model=dict)
async def get_sessions_list(
    status: Optional[str] = Query(None, description="按状态过滤：ongoing, completed"),
    skip: int = Query(0, description="分页起始偏移量"),
    limit: int = Query(20, le=100, description="每页返回数量，最大100"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 分页获取我的历史练习会话记录"""
    result = await ps_service.get_paginated_sessions(
        db=db, 
        user_id=current_student["id"], 
        status=status, 
        skip=skip, 
        limit=limit
    )
    
    # 格式化输出，处理 join 拿到的 bank 属性
    formatted_items = []
    for item in result["items"]:
        dump_data = PracticeSessionOut.model_validate(item).model_dump()
        dump_data["bank_name"] = item.bank.bank_name if hasattr(item, 'bank') and item.bank else "未知题库"
        formatted_items.append(dump_data)
        
    return success(data={"items": formatted_items, "total": result["total"]})

@router.get("/{session_id}")
async def get_practice_session_progress(
    session_id: int = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 恢复上次中断的练习进度 / 查询会话详情"""
    result = await ps_service.get_session_detail(
        db=db, session_id=session_id, user_id=current_student["id"]
    )
    return success(data=PracticeSessionOut.model_validate(result).model_dump(), message="获取练习进度成功")

@router.patch("/{session_id}/submit")
async def submit_practice_session(
    session_id: int = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 主动交卷（结束会话）"""
    await ps_service.submit_session(
        db=db, session_id=session_id, user_id=current_student["id"]
    )
    return success(message="交卷成功，会话已结束")

@router.delete("/")
async def delete_practice_sessions(
    payload: BatchDeleteSessionReq,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """[学生端] 批量删除练习会话记录"""
    await ps_service.delete_user_sessions(
        db=db, session_ids=payload.ids, user_id=current_student["id"]
    )
    return success(message=f"成功删除 {len(payload.ids)} 条会话")