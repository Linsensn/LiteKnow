# backend/routers/student_sessions.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from config.database import get_db  
from utils.deps import get_current_user  
from utils.response import success, fail  
from utils.exceptions import CustomAPIException, ErrorCode  
from schemas import session_schemas
from crud import session_crud
from models.users import User  

router = APIRouter(prefix="/sessions", tags=["Student/Sessions"])

@router.post("/", summary="新建会话")
def create_my_session(
    data: session_schemas.SessionCreate, 
    db: DBSession = Depends(get_db), 
    user: User = Depends(get_current_user)  
):
    session = session_crud.create_session(db, user_id=user.id, obj_in=data.model_dump())
    return success(data=session_schemas.SessionOut.model_validate(session).model_dump())  

@router.get("/", summary="多条件查询我的会话")
def read_my_sessions(
    skip: int = 0, limit: int = 20, keyword: str = None, task_type: str = None,
    db: DBSession = Depends(get_db), user: User = Depends(get_current_user)  
):
    sessions = session_crud.get_sessions(db, skip=skip, limit=limit, user_id=user.id, keyword=keyword, task_type=task_type)
    return success(data=[session_schemas.SessionOut.model_validate(s).model_dump() for s in sessions])  

@router.delete("/{session_id}", summary="逻辑删除我的会话")
def delete_my_session(session_id: int, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):  
    session = session_crud.get_session_by_id(db, session_id)
    if not session or session.user_id != user.id:  
        raise CustomAPIException(ErrorCode.NOT_FOUND, message="会话不存在或无权操作")  
    
    session_crud.soft_delete_session(db, session)
    return success(message="会话已删除")  