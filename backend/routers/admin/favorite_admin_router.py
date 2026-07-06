# backend/routers/admin/favorites_admin_route.py
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from config.database import get_db
from utils.deps import get_admin_user
from utils.response import success
from schemas.common import ResponseModel, PageResult
from schemas.favorites import FavoriteResponse, FavoriteAdminBatchDeleteReq
from services.favorite_service import fav_service

router = APIRouter(prefix="/favorites", tags=["Admin - 收藏管理"])


@router.get(
    "",
    summary="全量分页查询收藏夹",
    response_model=ResponseModel[PageResult[FavoriteResponse]]
)
async def get_folders_admin(
    content_type: Optional[str] = Query(None, description="筛选类型: question(题目)/summary(摘要)/knowledge(知识点)"),
    user_id: Optional[int] = Query(None, description="筛选所属用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    data = await fav_service.get_folders_admin(
        db, page=page, page_size=page_size,
        content_type=content_type, user_id=user_id
    )
    return success(data=data)


@router.get(
    "/{folder_id}",
    summary="获取单个收藏夹详情",
    response_model=ResponseModel[FavoriteResponse]
)
async def get_folder_admin(
    folder_id: int = Path(..., description="收藏夹ID"),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    folder = await fav_service.get_folder_admin(db, folder_id=folder_id)
    return success(data=folder)


@router.get(
    "/top",
    summary="获取全站收藏夹热度 Top N",
    response_model=ResponseModel[dict]
)
async def get_top_favorites(
    limit: int = Query(10, le=50, description="获取前N名"),
    content_type: Optional[str] = Query(None, description="筛选类型: question(题目)/summary(摘要)/knowledge(知识点)"),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    top_items = await fav_service.get_top_favorites(db, limit=limit, content_type=content_type)
    return success(data={"top_favorites": top_items})


@router.delete(
    "/batch",
    summary="批量删除收藏夹",
    response_model=ResponseModel[dict]
)
async def batch_delete_folders_admin(
    req: FavoriteAdminBatchDeleteReq,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_admin_user)
):
    count = await fav_service.batch_delete_admin(db, ids=req.ids)
    return success(data={"deleted_count": count}, message=f"成功删除{count}个收藏夹")