# backend/schemas/favorites.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any 
from datetime import datetime


class FavoriteBase(BaseModel):
    content_type: str = Field(..., description="收藏类型: question/summary/knowledge")
    cover_image_url: Optional[str] = Field(None, description="收藏夹封面/缩略图")
    source_session: Optional[int] = Field(None, description="来源会话ID，方便追溯")


class FavoriteCreate(FavoriteBase):
    """系统内部创建收藏夹使用，学生端不暴露创建接口"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content_type": "question",
                "cover_image_url": "https://oss.example.com/covers/xxx.jpg",
                "source_session": 1024
            }
        }
    )



class FavoriteUpdate(BaseModel):
    cover_image_url: Optional[str] = Field(None, description="收藏夹封面/缩略图")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cover_image_url": "https://oss.example.com/covers/new_cover.jpg"
            }
        }
    )

class FavoriteResponse(FavoriteBase):
    id: int = Field(..., description="收藏夹ID")
    user_id: int = Field(..., description="所属用户ID")
    content_ids: List[int] = Field(..., description="收藏夹内的内容ID数组")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 8848,
                "content_type": "question",
                "cover_image_url": "https://oss.example.com/covers/xxx.jpg",
                "source_session": 1024,
                "content_ids": [5001, 5002, 5003],
                "created_at": "2026-07-05T21:30:00",
                "updated_at": "2026-07-05T22:00:00"
            }
        }
    )

# 切换收藏/单条内容操作请求体
class FavoriteContentOperateReq(BaseModel):
    content_type: str = Field(..., description="收藏夹类型: 题目/摘要")
    content_id: int = Field(..., description="要添加/移除的内容ID")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content_type": "question",
                "content_id": 5001
            }
        }
    )

# 批量移除内容请求体
class FavoriteBatchRemoveReq(BaseModel):
    content_ids: List[int] = Field(..., description="要移除的内容ID列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content_ids": [5001, 5002, 5003]
            }
        }
    )

# 管理端批量删除收藏夹请求体
class FavoriteAdminBatchDeleteReq(BaseModel):
    ids: List[int] = Field(..., description="要删除的收藏夹ID列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [1, 2, 3]
            }
        }
    )

# ──────────── 收藏状态查询 ────────────

class FavoriteStatusResponse(BaseModel):
    """单条内容收藏状态"""
    is_favorited: bool = Field(..., description="是否已收藏")
    folder_id: Optional[int] = Field(None, description="所属收藏夹ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_favorited": True,
                "folder_id": 1
            }
        }
    )

class BatchFavStatusRequest(BaseModel):
    """批量查询收藏状态请求"""
    content_type: str = Field(..., description="收藏类型: question/summary/knowledge")
    content_ids: List[int] = Field(..., description="要查询状态的内容ID列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content_type": "question",
                "content_ids": [5001, 5002, 5003]
            }
        }
    )

class BatchFavStatusResponse(BaseModel):
    """批量查询收藏状态响应"""
    status_map: dict[str, bool] = Field(..., description="内容ID → 是否收藏")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status_map": {"5001": True, "5002": False, "5003": True}
            }
        }
    )

class FolderContentsResponse(BaseModel):
    """收藏夹内容详情（含解析后的具体内容）"""
    folder: FavoriteResponse = Field(..., description="收藏夹元信息")
    contents: List[Any] = Field(default=[], description="内容列表（按content_type返回对应结构）")
    total: int = Field(..., description="内容总数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "folder": {
                    "id": 1, "content_type": "question", "content_ids": [5001, 5002],
                    "cover_image_url": "...", "created_at": "2026-07-05T21:30:00"
                },
                "contents": [
                    {"id": 5001, "content": "1+1等于几？", "question_type": "single_choice"}
                ],
                "total": 2, "page": 1, "page_size": 20
            }
        }
    )   
