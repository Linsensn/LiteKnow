# backend/routers/admin/favorites_admin_route.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.deps import get_admin_user
from utils.response import success
from schemas.common import ResponseModel
from services.favorite_service import fav_service

router = APIRouter(prefix="/favorites", tags=["Admin - 收藏分析"])


@router.get("/top", summary="获取全站收藏 Top N", response_model=ResponseModel[dict])
async def get_top_favorites(
    limit: int = Query(10, le=50, description="获取前N名"),
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_admin_user)
):
    top_items = await fav_service.get_top_favorites(db, limit=limit)
    return success(data={"top_favorites": top_items})