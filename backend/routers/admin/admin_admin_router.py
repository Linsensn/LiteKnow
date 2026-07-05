# backend/routers/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db 
from utils.response import success 
from utils.exceptions import CustomAPIException, ErrorCode 
from schemas.schemas_user import UserUpdate, UserOut 
from crud import crud_user
from models.users import User

# 全局注入 get_admin_user 拦截器，确保下方所有接口都需要管理员权限
router = APIRouter(
    prefix="/users", 
    tags=["Admin/Users"]
)

@router.get("/", summary="分页获取所有用户列表")
def read_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)): 
    users = crud_user.get_users(db, skip=skip, limit=limit)
    data = [UserOut.model_validate(u).model_dump() for u in users] 
    return success(data=data) 

@router.get("/{user_id}", summary="查询指定用户信息")
def read_user_by_id(user_id: int, db: Session = Depends(get_db)): 
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise CustomAPIException(ErrorCode.USER_NOT_FOUND) 
    return success(data=UserOut.model_validate(user).model_dump()) 

@router.put("/{user_id}", summary="修改指定用户信息")
def update_user_by_admin(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)): #[cite: 18, 19]
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise CustomAPIException(ErrorCode.USER_NOT_FOUND) 
    
    update_dict = update_data.model_dump(exclude_unset=True) 
    updated_user = crud_user.update_user(db, db_user=user, update_data=update_dict)
    return success(data=UserOut.model_validate(updated_user).model_dump(), message="管理员更新用户资料成功") 

@router.delete("/{user_id}", summary="删除指定用户")
def delete_user_by_admin(user_id: int, db: Session = Depends(get_db)): 
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise CustomAPIException(ErrorCode.USER_NOT_FOUND) 
        
    crud_user.delete_user(db, db_user=user)
    return success(message=f"已成功删除用户 (ID: {user_id})") 