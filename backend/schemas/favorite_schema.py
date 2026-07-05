# backend/schemas/favorites.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime


class FavoriteBase(BaseModel):
    content_type: str = Field(..., description="收藏类型: question/summary/knowledge")
    content_id: int = Field(..., description="关联的源数据ID，与content_type对应不同业务表")
    cover_image_url: Optional[str] = Field(None, description="列表展示用的封面/缩略图")
    source_session: Optional[int] = Field(None, description="来源会话ID")


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)