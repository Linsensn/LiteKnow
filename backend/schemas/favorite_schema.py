# backend/schemas/favorites.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class FavoriteBase(BaseModel):
    content_type: str = Field(..., description="收藏类型: question/summary/knowledge")
    cover_image_url: Optional[str] = Field(None, description="收藏夹封面/缩略图")
    source_session: Optional[int] = Field(None, description="来源会话ID，方便追溯")


class FavoriteCreate(FavoriteBase):
    """系统内部创建收藏夹使用，学生端不暴露创建接口"""
    pass


class FavoriteUpdate(BaseModel):
    cover_image_url: Optional[str] = Field(None, description="收藏夹封面/缩略图")


class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    content_ids: List[int] = Field(..., description="收藏夹内的内容ID数组")
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# 切换收藏/单条内容操作请求体
class FavoriteContentOperateReq(BaseModel):
    content_type: str = Field(..., description="收藏夹类型: 题目/摘要")
    content_id: int = Field(..., description="要添加/移除的内容ID")


# 批量移除内容请求体
class FavoriteBatchRemoveReq(BaseModel):
    content_ids: List[int] = Field(..., description="要移除的内容ID列表")


# 管理端批量删除收藏夹请求体
class FavoriteAdminBatchDeleteReq(BaseModel):
    ids: List[int] = Field(..., description="要删除的收藏夹ID列表")