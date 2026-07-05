# backend/routers/student.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from utils.deps import get_current_user 
from utils.response import success 
from schemas.user_schemas import WeChatLogin, UserUpdate, UserOut 
from schemas.common import ResponseModel, PageResult
from services import user_service
from crud import user_crud
from models.users import User

router = APIRouter(tags=["Student/Users"])

@router.post("/auth/wechat", summary="微信静默登录/注册", response_model=ResponseModel[dict])
async def student_wechat_login(data: WeChatLogin, db: Session = Depends(get_db)): 
    token_data = await user_service.wechat_login_service(db, data.code)
    return success(data=token_data, message="登录成功") 

@router.get("/users/me", summary="获取个人信息", dependencies=[Depends(get_current_user)], 
            response_model=ResponseModel[UserOut])
def get_my_profile(current_user: User = Depends(get_current_user)): 
    # 使用 Pydantic 的 model_validate 将 ORM 对象转为标准 Schema 字典，再交给 success 包裹
    return success(data=UserOut.model_validate(current_user).model_dump()) 

@router.put("/users/me", summary="修改个人信息", dependencies=[Depends(get_current_user)], 
            response_model=ResponseModel[UserOut])
def update_my_profile(
    update_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) 
):
    update_dict = update_data.model_dump(exclude_unset=True) 
    updated_user = user_crud.update_user(db, db_user=current_user, update_data=update_dict)
    return success(data=UserOut.model_validate(updated_user).model_dump(), message="资料更新成功") 

@router.delete("/users/me", summary="注销个人账号", response_model=ResponseModel[dict])
def delete_my_account(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    合规要求：允许用户主动注销账号。
    执行逻辑删除，防止破坏与其关联的错题本、测验记录等外键约束。
    """
    user_crud.soft_delete_user(db, db_user=current_user)
    return success(message="账号已成功注销，感谢您的使用")