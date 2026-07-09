# backend/crud/favorites_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete, update
from typing import List, Optional
from models.favorites import Favorite


class CRUDFavorite:

    # 1. 按主键ID查询单个收藏夹
    # 可选传入 user_id 做归属校验，学生端调用时必传，防止越权
    async def get(self, db: AsyncSession, *, folder_id: int, user_id: Optional[int] = None) -> Optional[Favorite]:
        """"按主键ID查询单个收藏夹"""
        stmt = select(Favorite).where(Favorite.id == folder_id)
        if user_id:
            stmt = stmt.where(Favorite.user_id == user_id)
        result = db.execute(stmt)
        return result.scalars().first() 

    # 2. 按收藏类型获取用户的对应收藏夹
    # 用于收藏切换时自动定位默认夹，每个用户每类仅一个收藏夹
    async def get_by_type(
        self, db: AsyncSession, *, user_id: int, content_type: str
    ) -> Optional[Favorite]:
        """"按收藏类型获取用户的对应收藏夹"""
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.content_type == content_type
        )
        result = db.execute(stmt)
        return result.scalars().first() 

    # 3. 学生端：分页获取用户收藏夹列表
    # 支持按收藏类型筛选，按创建时间倒序排列
    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 20,
        content_type: Optional[str] = None
    ) -> List[Favorite]:
        """"学生端：分页获取用户收藏夹列表"""
        stmt = select(Favorite).where(Favorite.user_id == user_id)
        if content_type:
            stmt = stmt.where(Favorite.content_type == content_type)
        stmt = stmt.order_by(desc(Favorite.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    # 4. 学生端：统计用户收藏夹总数
    # 筛选条件与分页查询完全对齐，用于分页总页数计算
    async def count(
        self, db: AsyncSession, *, user_id: int, content_type: Optional[str] = None
    ) -> int:
        """"学生端：统计用户收藏夹总数"""
        stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        if content_type:
            stmt = stmt.where(Favorite.content_type == content_type)
        result = db.execute(stmt)
        return result.scalar() or 0

    # 5. 新建收藏夹
    # 初始化 content_ids 为空数组，自动关联所属用户
    async def create(self, db: AsyncSession, *, user_id: int, obj_in: dict) -> Favorite:
        """"新建收藏夹"""
        db_obj = Favorite(
            user_id=user_id,
            content_type=obj_in["content_type"],
            cover_image_url=obj_in.get("cover_image_url"),
            content_ids=[]
        )
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    # 6. 更新收藏夹基础信息
    # 仅更新传入的非空字段，支持修改封面、名称等属性
    async def update(self, db: AsyncSession, *, db_obj: Favorite, update_data: dict):
        """"更新收藏夹基础信息"""
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    # 7. 往收藏夹添加单条内容
    # 自动去重，返回 True 表示新增成功，False 表示内容已存在
    # 兜底空值：兼容历史脏数据中 content_ids 为 None 的场景
    async def add_content(self, db: AsyncSession, *, db_obj: Favorite, content_id: int) -> bool:
        """"往收藏夹添加单条内容"""
        current = db_obj.content_ids or []       # 兜底 None
        if content_id not in current:
            db_obj.content_ids = current + [content_id]  # ★ 新列表 → 触发脏追踪
            db.flush()
            return True
        return False

    # 8. 从收藏夹移除单条内容
    # 返回 True 表示移除成功，False 表示内容不存在
    async def remove_content(self, db: AsyncSession, *, db_obj: Favorite, content_id: int) -> bool:
        """"从收藏夹移除单条内容"""
        current = db_obj.content_ids or []       # 兜底 None
        if content_id in current:
            db_obj.content_ids = [cid for cid in current if cid != content_id]  # ★ 新列表
            db.flush()
            return True
        return False

    # 9. 从收藏夹批量移除内容
    # 返回实际成功移除的内容数量
    async def remove_contents_batch(self, db: AsyncSession, *, db_obj: Favorite, content_ids: List[int]) -> int:
        """"从收藏夹批量移除内容"""
        if db_obj.content_ids is None:
            db_obj.content_ids = []
        original_len = len(db_obj.content_ids)
        db_obj.content_ids = [cid for cid in db_obj.content_ids if cid not in content_ids]
        db.flush()
        return original_len - len(db_obj.content_ids)

    # 10. 物理删除单个收藏夹
    async def delete(self, db: AsyncSession, *, db_obj: Favorite):
        """"物理删除单个收藏夹"""
        db.delete(db_obj)
        db.flush()

    # 11. 批量删除收藏夹（学生端带用户归属校验）
    # 仅删除当前用户名下的收藏夹，防止越权操作，返回成功删除数量
    async def delete_by_ids(
        self, db: AsyncSession, *, user_id: int, ids: List[int]
    ) -> int:
        """"批量删除收藏夹（学生端带用户归属校验）"""
        stmt = delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.id.in_(ids)
        )
        result = db.execute(stmt)
        db.flush()
        return result.rowcount
    
    # 【补充】12. 管理端：批量删除收藏夹（无用户归属校验）
    # 权限由路由层依赖注入保证，仅管理员可调用，直接按ID列表删除
    async def delete_by_ids_admin(self, db: AsyncSession, *, ids: List[int]) -> int:
        """"管理端：批量删除收藏夹（无用户归属校验）"""
        stmt = delete(Favorite).where(Favorite.id.in_(ids))
        result = db.execute(stmt)
        db.flush()
        return result.rowcount
    
    # 12. 管理端：收藏夹热度排行
    # 按收藏内容数量倒序排序，支持按收藏类型筛选，用于运营分析
    async def get_top_favorites(self, db: AsyncSession, limit: int = 10, content_type: Optional[str] = None):
        """"收藏夹热度排行"""
        stmt = select(
            Favorite.id,
            Favorite.content_type,
            func.json_length(Favorite.content_ids).label('content_count')
        )
        if content_type:
            stmt = stmt.where(Favorite.content_type == content_type)
        stmt = stmt.order_by(desc('content_count')).limit(limit)
        result = db.execute(stmt)
        return result.all()

    # 13. 管理端：全量分页查询收藏夹
    # 支持按收藏类型、所属用户ID筛选，按创建时间倒序
    async def get_multi_admin(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 20,
        content_type: Optional[str] = None, user_id: Optional[int] = None
    ) -> List[Favorite]:
        """全量分页查询收藏夹"""
        stmt = select(Favorite)
        if content_type:
            stmt = stmt.where(Favorite.content_type == content_type)
        if user_id:
            stmt = stmt.where(Favorite.user_id == user_id)
        stmt = stmt.order_by(desc(Favorite.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    # 14. 管理端：统计符合条件的收藏夹总数
    # 筛选条件与全量分页查询完全对齐，用于管理端分页计算
    async def count_admin(
        self, db: AsyncSession, *, content_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> int:
        """"筛选条件与全量分页查询完全对齐，用于管理端分页计算"""
        stmt = select(func.count(Favorite.id))
        if content_type:
            stmt = stmt.where(Favorite.content_type == content_type)
        if user_id:
            stmt = stmt.where(Favorite.user_id == user_id)
        result = db.execute(stmt)
        return result.scalar() or 0


favorite_crud = CRUDFavorite()