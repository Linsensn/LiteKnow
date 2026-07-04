# backend/routers/student.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from utils.deps import get_current_user 
from utils.response import success 
from schemas.schemas_user import WeChatLogin, UserUpdate, UserOut 
from services import user_service
from crud import crud_user
from models.users import User

router = APIRouter(tags=["Student/Users"])

@router.post("/auth/wechat", summary="微信静默登录/注册")
async def student_wechat_login(data: WeChatLogin, db: Session = Depends(get_db)): 
    token_data = await user_service.wechat_login_service(db, data.code)
    return success(data=token_data, message="登录成功") 

@router.get("/users/me", summary="获取个人信息")
def get_my_profile(current_user: User = Depends(get_current_user)): 
    # 使用 Pydantic 的 model_validate 将 ORM 对象转为标准 Schema 字典，再交给 success 包裹
    return success(data=UserOut.model_validate(current_user).model_dump()) 

@router.put("/users/me", summary="修改个人信息")
def update_my_profile(
    update_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) 
):
    update_dict = update_data.model_dump(exclude_unset=True) 
    updated_user = crud_user.update_user(db, db_user=current_user, update_data=update_dict)
    return success(data=UserOut.model_validate(updated_user).model_dump(), message="资料更新成功") 