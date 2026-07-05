# backend/routers/student/favorites_student_route.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from config.database import get_db
from utils.deps import get_current_user
from utils.response import success
from services.favorite_service import fav_service
from schemas.favorite_schema import FavoriteCreate

router = APIRouter(prefix="/favorites", tags=["Student - 收藏夹"])


@router.post("/toggle", summary="切换收藏状态")
async def toggle_favorite(
    fav_in: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    result = await fav_service.toggle_favorite(
        db, user_id=current_student["id"], obj_in=fav_in
    )
    return success(data={"action": result["action"]}, message=result["message"])


@router.get("", summary="分页获取我的收藏列表")
async def get_my_favorites(
    content_type: Optional[str] = Query(None, description="筛选类型: question/summary/knowledge"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    data = await fav_service.get_my_favorites(
        db, user_id=current_student["id"], content_type=content_type,
        page=page, page_size=page_size
    )
    return success(data=data)