# backend/services/favorite_service.py
import json
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from crud.favorites_crud import favorite_crud
from schemas.favorite_schema import FavoriteCreate

class FavoriteService:

    # 1. 收藏/取消收藏 状态切换
    async def toggle_favorite(self, db: AsyncSession, user_id: int, obj_in: FavoriteCreate):
        content_str = json.dumps(obj_in.content_data, ensure_ascii=False)
        try:
            existing_fav = await favorite_crud.get_by_content(
                db, user_id=user_id, content_type=obj_in.content_type, content_data_str=content_str
            )

            if existing_fav:
                await favorite_crud.delete(db, db_obj=existing_fav)
                await db.commit()
                return {"action": "removed", "message": "已取消收藏"}
            else:
                create_data = {
                    "user_id": user_id,
                    "content_type": obj_in.content_type,
                    "cover_image_url": obj_in.cover_image_url,
                    "content_data": content_str,
                    "source_session": obj_in.source_session
                }
                await favorite_crud.create(db, obj_in=create_data)
                await db.commit()
                return {"action": "added", "message": "收藏成功"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    # 2. 分页获取我的收藏列表
    async def get_my_favorites(
        self, db: AsyncSession, user_id: int, content_type: str = None,
        page: int = 1, page_size: int = 20
    ):
        skip = (page - 1) * page_size
        total = await favorite_crud.count(db, user_id=user_id, content_type=content_type)
        items = await favorite_crud.get_multi_by_user(
            db, user_id=user_id, content_type=content_type, skip=skip, limit=page_size
        )

        # 数据库存储为 JSON 字符串，返回前端前反序列化为字典
        for item in items:
            if isinstance(item.content_data, str):
                item.content_data = json.loads(item.content_data)

        return {"total": total, "items": items}

    # 3. 管理端：获取全站收藏 Top N
    async def get_top_favorites(self, db: AsyncSession, limit: int = 10):
        raw_list = await favorite_crud.get_top_favorites(db, limit=limit)
        result = []
        for row in raw_list:
            result.append({
                "content_type": row.content_type,
                "content_data": json.loads(row.content_data),
                "fav_count": row.fav_count
            })
        return result


fav_service = FavoriteService()