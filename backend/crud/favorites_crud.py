# backend/crud/crud_favorites.py
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete
from typing import List, Optional
from models.favorites import Favorite


class CRUDFavorite:

    # 1. 分页获取用户收藏列表
    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 20,
        content_type: Optional[str] = None
    ) -> List[Favorite]:
        stmt = select(Favorite).where(Favorite.user_id == user_id)
        if content_type:
            stmt = stmt.where(Favorite.content_type == content_type)
        stmt = stmt.order_by(desc(Favorite.created_at)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    # 2. 统计用户收藏总数（配合分页）
    async def count(
        self, db: AsyncSession, *, user_id: int, content_type: Optional[str] = None
    ) -> int:
        stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        if content_type:
            stmt = stmt.where(Favorite.content_type == content_type)
        result = await db.execute(stmt)
        return result.scalar_one()

    # 3. 根据内容精确匹配单条记录（用于 Toggle 判断）
    async def get_by_content(
        self, db: AsyncSession, *, user_id: int, content_type: str, content_data_str: str
    ) -> Optional[Favorite]:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.content_type == content_type,
            Favorite.content_data == content_data_str
        )
        result = await db.execute(stmt)
        return result.scalar_first()

    # 4. 新增单条收藏
    async def create(self, db: AsyncSession, *, obj_in: dict) -> Favorite:
        db_obj = Favorite(**obj_in)
        db.add(db_obj)
        await db.flush()
        return db_obj

    # 5. 删除单条收藏
    async def delete(self, db: AsyncSession, *, db_obj: Favorite):
        await db.delete(db_obj)
        await db.flush()

    # 6. 管理端：全站收藏 Top N 聚合统计
    async def get_top_favorites(self, db: AsyncSession, limit: int = 10):
        stmt = select(
            Favorite.content_data,
            Favorite.content_type,
            func.count(Favorite.id).label('fav_count')
        ).group_by(
            Favorite.content_data,
            Favorite.content_type
        ).order_by(desc('fav_count')).limit(limit)
        result = await db.execute(stmt)
        return result.all()


favorite_crud = CRUDFavorite()