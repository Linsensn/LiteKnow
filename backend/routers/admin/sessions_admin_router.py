# backend/routers/admin_sessions.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from config.database import get_db  
from utils.deps import get_admin_user  
from utils.response import success  
from schemas.session_schemas import SessionCreate, SessionStatusToggle, SessionOut
from schemas.common import ResponseModel, PageResult
from crud import session_crud
from services import session_service
from models.users import User

router = APIRouter(prefix="/sessions", tags=["Admin/Sessions"])

@router.get("/", summary="全局分页与关联查询", response_model=ResponseModel[PageResult[SessionOut]])
def read_all_sessions(
    page: int = 1, page_size: int = 20, keyword: str = None, user_id: int = None,
    db: DBSession = Depends(get_db), admin: User = Depends(get_admin_user)
):
    skip = (page - 1) * page_size
    total, sessions = session_crud.get_sessions_paginated(
        db, skip=skip, limit=page_size, user_id=user_id, keyword=keyword
    )
    
    data_list = [SessionOut.model_validate(s).model_dump() for s in sessions]
    page_data = PageResult(list=data_list, total=total, page=page, page_size=page_size)
    
    return success(data=page_data.model_dump())

@router.post("/batch", summary="批量新建会话", response_model=ResponseModel[dict])
def batch_create_sessions(
    target_user_id: int, data_list: list[SessionCreate], 
    db: DBSession = Depends(get_db), admin: User = Depends(get_admin_user)  
):
    count = session_crud.batch_create_sessions(db, user_id=target_user_id, objs_in=[d.model_dump() for d in data_list])
    session_service.audit_log(admin.id, "BATCH_CREATE", details=f"Created {count} sessions for user {target_user_id}")
    return success(message=f"成功批量创建 {count} 条会话")  

@router.put("/batch/status", summary="批量状态切换", response_model=ResponseModel[dict])
def batch_update_status(
    session_ids: list[int], status_data: SessionStatusToggle, 
    db: DBSession = Depends(get_db), admin: User = Depends(get_admin_user)  
):
    count = session_crud.batch_update_status(db, session_ids, status_data.status)
    session_service.audit_log(admin.id, "BATCH_UPDATE_STATUS", details=f"Updated {count} sessions to {status_data.status}")
    return success(message=f"成功切换 {count} 条会话状态")  

@router.delete("/batch", summary="批量物理/逻辑删除", response_model=ResponseModel[dict])
def batch_delete_sessions(
    session_ids: list[int], physical: bool = False, 
    db: DBSession = Depends(get_db), admin: User = Depends(get_admin_user)  
):
    session_crud.batch_delete_sessions(db, session_ids, physical=physical)
    session_service.audit_log(admin.id, "BATCH_DELETE", details=f"Deleted {len(session_ids)} sessions. Physical: {physical}")
    return success(message=f"成功删除 {len(session_ids)} 条会话")  

@router.get("/statistics/task_type", summary="聚合计算：按任务类型统计", response_model=ResponseModel[list[dict]])
def get_statistics(db: DBSession = Depends(get_db)):  
    stats = session_crud.get_task_type_statistics(db)
    # 将 SQLAlchemy 返回的 Row 对象转换为列表字典
    return success(data=[{"task_type": row[0], "count": row[1]} for row in stats])  

@router.get("/export", summary="数据导出", response_model=ResponseModel[dict])
async def export_sessions(db: DBSession = Depends(get_db)):  
    return await session_service.export_sessions_csv(db)