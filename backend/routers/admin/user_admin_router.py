# backend/routers/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db 
from utils.response import success 
from utils.deps import get_admin_user 
from utils.exceptions import CustomAPIException, ErrorCode 
from schemas.user_schemas import UserUpdate, UserOut, UserCreate, UserStatusToggle
from schemas.common import ResponseModel, PageResult
from crud import user_crud
from services import user_service
from models.users import User

router = APIRouter(prefix="/users", tags=["Admin/Users"])

@router.post("/", summary="手动创建单条用户", response_model=ResponseModel[UserOut])
def create_user_manual(data: UserCreate, db: Session = Depends(get_db)):
    # 绕过微信体系手动建号
    user = user_crud.create_user(db, openid=data.wechat_openid or "manual_create", role=data.role)
    user_crud.update_user(db, db_user=user, update_data={"nickname": data.nickname, "is_active": data.is_active})
    return success(data=UserOut.model_validate(user).model_dump())

@router.post("/batch", summary="批量导入/新建用户", response_model=ResponseModel[dict])
def batch_create_users(data_list: list[UserCreate], db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    count = user_crud.batch_create_users(db, objs_in=[d.model_dump() for d in data_list])
    user_service.audit_log(admin.id, "BATCH_CREATE_USERS", details=f"Count: {count}")
    return success(message=f"成功批量导入 {count} 名用户")

@router.get("/", summary="分页获取所有用户列表", response_model=ResponseModel[PageResult[UserOut]])
def read_users(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    skip = (page - 1) * page_size 
    total, users = user_crud.get_users_paginated(db, skip=skip, limit=page_size)
    
    page_data = PageResult[UserOut](
        list=[UserOut.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )
    return success(data=page_data)

@router.get("/{user_id}", summary="查询指定用户信息", response_model=ResponseModel[UserOut])
def read_user_by_id(user_id: int, db: Session = Depends(get_db)): 
    user = user_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise CustomAPIException(ErrorCode.USER_NOT_FOUND) 
    return success(data=UserOut.model_validate(user).model_dump()) 

@router.put("/{user_id}", summary="修改指定用户信息", response_model=ResponseModel[UserOut])
def update_user_by_admin(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise CustomAPIException(ErrorCode.USER_NOT_FOUND) 
    
    update_dict = update_data.model_dump(exclude_unset=True) 
    updated_user = user_crud.update_user(db, db_user=user, update_data=update_dict)
    return success(data=UserOut.model_validate(updated_user).model_dump(), message="管理员更新用户资料成功") 

@router.put("/batch/status", summary="批量状态切换(封禁/解封)", response_model=ResponseModel[dict])
def batch_update_user_status(
    user_ids: list[int], status_data: UserStatusToggle, 
    db: Session = Depends(get_db), admin: User = Depends(get_admin_user)
):
    count = user_crud.batch_update_status(db, user_ids, status_data.is_active)
    action_str = "解封" if status_data.is_active else "封禁"
    user_service.audit_log(admin.id, "BATCH_UPDATE_STATUS", details=f"{action_str} {count} users")
    return success(message=f"成功{action_str} {count} 名用户")

@router.delete("/{user_id}", summary="逻辑删除指定用户", response_model=ResponseModel[dict])
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    user = user_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise CustomAPIException(ErrorCode.USER_NOT_FOUND)
        
    user_crud.soft_delete_user(db, db_user=user)
    user_service.audit_log(admin.id, "SOFT_DELETE_USER", details=f"Target UserID: {user_id}")
    return success(message=f"已成功注销用户 (ID: {user_id})")

@router.delete("/batch/delete", summary="批量删除用户(支持物理抹除)", response_model=ResponseModel[dict])
def batch_delete_users(
    user_ids: list[int], physical: bool = False, 
    db: Session = Depends(get_db), admin: User = Depends(get_admin_user)
):
    user_crud.batch_delete_users(db, user_ids, physical=physical)
    user_service.audit_log(admin.id, "BATCH_DELETE_USERS", details=f"Count: {len(user_ids)}, Physical: {physical}")
    return success(message=f"成功删除 {len(user_ids)} 名用户")

# 聚合与导出 
@router.get("/data/statistics", summary="聚合计算：按角色分类统计", response_model=ResponseModel[list[dict]])
def get_user_statistics(db: Session = Depends(get_db)):
    stats = user_crud.get_role_statistics(db)
    return success(data=[{"role": row[0], "count": row[1]} for row in stats])

@router.get("/data/export", summary="数据导出：下载用户报表 CSV", response_model=ResponseModel[dict])
async def export_users_data(db: Session = Depends(get_db)):
    return await user_service.export_users_csv(db)