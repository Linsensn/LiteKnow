# backend/routers/student/favorites_student_route.py
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from config.database import get_db
from utils.deps import get_current_user
from utils.response import success
from schemas.common import ResponseModel, PageResult
from schemas.favorites import (
    FavoriteResponse,
    FavoriteUpdate,
    FavoriteContentOperateReq,
    FavoriteBatchRemoveReq
)
from services.favorite_service import fav_service

router = APIRouter(prefix="/favorites", tags=["Student - favorites"])


@router.post(
    "/toggle",
    summary="切换收藏状态",
    response_model=ResponseModel[dict]
)
async def toggle_favorite(
    req: FavoriteContentOperateReq,
    db: AsyncSession = Depends(get_db),
    current_student = Depends(get_current_user)
):
    result = await fav_service.toggle_favorite(
        db, user_id=current_student.id, content_type=req.content_type, content_id=req.content_id
    )
    return success(data={"action": result["action"]}, message=result["message"])

@router.post(
    "/toggle",
    summary="切换收藏状态",
    response_model=ResponseModel[dict]
)
async def toggle_favorite(
    req: FavoriteContentOperateReq,
    db: AsyncSession = Depends(get_db),
    current_student = Depends(get_current_user)
):
    result = await fav_service.toggle_favorite(
        db, user_id=current_student.id, content_type=req.content_type, content_id=req.content_id
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
        db, user_id=current_student.id, content_type=content_type,
        page=page, page_size=page_size
    )
    return success(data=data)

@router.get(
    "/{folder_id}",
    summary="获取单个收藏夹详情",
    response_model=ResponseModel[FavoriteResponse]
)
async def get_folder_detail(
    folder_id: int = Path(..., description="收藏夹ID"),
    db: AsyncSession = Depends(get_db),
    current_student = Depends(get_current_user)
):
    folder = await fav_service.get_folder_detail(
        db, user_id=current_student.id, folder_id=folder_id
    )
    return success(data=folder)

@router.put(
    "/{folder_id}",
    summary="更新收藏夹基础信息",
    response_model=ResponseModel[FavoriteResponse]
)
async def update_folder(
    folder_id: int = Path(..., description="收藏夹ID"),
    update_in: FavoriteUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_student = Depends(get_current_user)
):
    folder = await fav_service.update_folder_info(
        db, user_id=current_student.id, folder_id=folder_id,
        update_data=update_in.model_dump(exclude_unset=True)
    )
    return success(data=folder)


@router.delete(
    "/contents/batch",
    summary="批量移除收藏夹内的内容",
    response_model=ResponseModel[dict]
)
async def batch_remove_contents(
    content_type: str = Query(..., description="收藏夹类型: question/summary/knowledge"),
    req: FavoriteBatchRemoveReq = ...,
    db: AsyncSession = Depends(get_db),
    current_student = Depends(get_current_user)
):
    count = await fav_service.batch_remove_contents(
        db, user_id=current_student.id, content_type=content_type, content_ids=req.content_ids
    )
    return success(data={"removed_count": count}, message=f"成功移除{count}条收藏内容")