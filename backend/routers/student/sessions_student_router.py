# backend/routers/student_sessions.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from config.database import get_db  
from utils.deps import get_current_user  
from utils.response import success, fail  
from utils.exceptions import CustomAPIException, ErrorCode  
from schemas.session_schemas import SessionCreate, SessionOut, SessionTreeOut, SessionUpdate
from schemas.common import ResponseModel, PageResult
from crud import session_crud
from models.users import User  

router = APIRouter(prefix="/sessions", tags=["Student/Sessions"])

@router.post("/", summary="新建会话", response_model=ResponseModel[SessionOut])
def create_my_session(
    data: SessionCreate, 
    db: DBSession = Depends(get_db), 
    user: User = Depends(get_current_user)  
):
    session = session_crud.create_session(db, user_id=user.id, obj_in=data.model_dump())
    return success(data=SessionOut.model_validate(session).model_dump())  

@router.get("/", summary="分页与多条件模糊查询", response_model=ResponseModel[PageResult[SessionOut]])
def read_my_sessions(
    page: int = 1, page_size: int = 20, keyword: str = None, task_type: str = None,
    db: DBSession = Depends(get_db), user: User = Depends(get_current_user)
):
    skip = (page - 1) * page_size
    total, sessions = session_crud.get_sessions_paginated(
        db, skip=skip, limit=page_size, user_id=user.id, keyword=keyword, task_type=task_type
    )
    
    data_list = [SessionOut.model_validate(s).model_dump() for s in sessions]
    page_data = PageResult(list=data_list, total=total, page=page, page_size=page_size)
    
    return success(data=page_data.model_dump())

@router.get("/tree", summary="树形查询我的会话", response_model=ResponseModel[list[SessionTreeOut]])
def read_my_sessions_tree(
    db: DBSession = Depends(get_db), user: User = Depends(get_current_user)
):
    # 获取顶层节点及其嵌套子节点
    tree_data = session_crud.get_sessions_tree(db, user_id=user.id)
    return success(data=[SessionTreeOut.model_validate(s).model_dump() for s in tree_data])

@router.put("/{session_id}", summary="单条更改我的会话", response_model=ResponseModel[SessionOut])
def update_my_session(
    session_id: int, update_data: SessionUpdate, 
    db: DBSession = Depends(get_db), user: User = Depends(get_current_user)
):
    session = session_crud.get_session_by_id(db, session_id)
    if not session or session.user_id != user.id:
        raise CustomAPIException(ErrorCode.NOT_FOUND, message="会话不存在或无权操作")
    
    updated_session = session_crud.update_session(db, db_obj=session, update_data=update_data.model_dump(exclude_unset=True))
    return success(data=SessionOut.model_validate(updated_session).model_dump())

@router.delete("/{session_id}", summary="逻辑删除我的会话", response_model=ResponseModel[dict])
def delete_my_session(session_id: int, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    session = session_crud.get_session_by_id(db, session_id)
    if not session or session.user_id != user.id:
        raise CustomAPIException(ErrorCode.NOT_FOUND, message="会话不存在或无权操作")
    
    session_crud.soft_delete_session(db, session)
    return success(message="会话已删除")