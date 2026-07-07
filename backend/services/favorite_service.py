# backend/services/favorite_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from crud.favorites_crud import favorite_crud
from schemas.favorite_schema import FavoriteCreate
from schemas.common import PageResult
from utils.exceptions import CustomAPIException, ErrorCode


class FavoriteService:

    # ==================== 学生端方法 ====================

    # 1. 收藏/取消收藏 状态切换
    # 自动定位对应类型的收藏夹，不存在则自动创建
    async def toggle_favorite(
        self, db: AsyncSession, user_id: int, obj_in: FavoriteCreate, content_id: int
    ):
        try:
            folder = await favorite_crud.get_by_type(
                db, user_id=user_id, content_type=obj_in.content_type
            )
            # 对应类型收藏夹不存在，自动创建默认夹
            if not folder:
                folder = await favorite_crud.create(db, user_id=user_id, obj_in=obj_in.model_dump())

            if content_id in folder.content_ids:
                await favorite_crud.remove_content(db, db_obj=folder, content_id=content_id)
                db.commit()
                return {"action": "removed", "message": "已取消收藏"}
            else:
                await favorite_crud.add_content(db, db_obj=folder, content_id=content_id)
                db.commit()
                return {"action": "added", "message": "收藏成功"}
        except Exception as e:
            db.rollback()
            raise CustomAPIException(
                code=ErrorCode.DB_OPERATION_FAILED,
                message=str(e)
            )

    # 2. 分页获取我的收藏夹列表
    async def get_my_folders(
        self, db: AsyncSession, user_id: int, content_type: str = None,
        page: int = 1, page_size: int = 20
    ):
        skip = (page - 1) * page_size
        total = await favorite_crud.count(db, user_id=user_id, content_type=content_type)
        items = await favorite_crud.get_multi_by_user(
            db, user_id=user_id, content_type=content_type, skip=skip, limit=page_size
        )
        return PageResult(
            list=items,
            total=total,
            page=page,
            page_size=page_size
        )

    # 3. 获取单个收藏夹详情（带用户归属校验）
    async def get_folder_detail(
        self, db: AsyncSession, user_id: int, folder_id: int
    ):
        folder = await favorite_crud.get(db, folder_id=folder_id, user_id=user_id)
        if not folder:
            raise CustomAPIException(
                code=ErrorCode.NOT_FOUND,
                message="收藏夹不存在"
            )
        return folder

    # 4. 更新收藏夹基础信息（封面等）
    async def update_folder_info(
        self, db: AsyncSession, user_id: int, folder_id: int, update_data: dict
    ):
        try:
            folder = await favorite_crud.get(db, folder_id=folder_id, user_id=user_id)
            if not folder:
                raise CustomAPIException(
                    code=ErrorCode.NOT_FOUND,
                    message="收藏夹不存在"
                )
            updated = await favorite_crud.update(db, db_obj=folder, update_data=update_data)
            db.commit()
            return updated
        except CustomAPIException:
            raise
        except Exception as e:
            db.rollback()
            raise CustomAPIException(
                code=ErrorCode.DB_OPERATION_FAILED,
                message=str(e)
            )

    # 5. 批量移除收藏夹内的内容
    async def batch_remove_contents(
        self, db: AsyncSession, user_id: int, content_type: str, content_ids: List[int]
    ) -> int:
        try:
            folder = await favorite_crud.get_by_type(db, user_id=user_id, content_type=content_type)
            if not folder:
                return 0
            count = await favorite_crud.remove_contents_batch(db, db_obj=folder, content_ids=content_ids)
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise CustomAPIException(
                code=ErrorCode.DB_OPERATION_FAILED,
                message=str(e)
            )

# ──────────── 收藏状态查询 ────────────

    # 6. 检查单条内容是否已收藏
    async def check_favorite_status(
        self, db: AsyncSession, user_id: int, content_type: str, content_id: int
    ) -> dict:
        """查单个内容收藏状态，前端用于详情页星星显示"""
        folder = await favorite_crud.get_by_type(db, user_id=user_id, content_type=content_type)
        if not folder:
            return {"is_favorited": False, "folder_id": None}
        return {
            "is_favorited": content_id in (folder.content_ids or []),
            "folder_id": folder.id
        }

    # 7. 批量检查收藏状态
    async def batch_check_status(
        self, db: AsyncSession, user_id: int, content_type: str, content_ids: List[int]
    ) -> dict:
        """批量查收藏状态，前端用于列表页批量标星"""
        folder = await favorite_crud.get_by_type(db, user_id=user_id, content_type=content_type)
        if not folder:
            return {str(cid): False for cid in content_ids}
        fav_set = set(folder.content_ids or [])
        return {str(cid): cid in fav_set for cid in content_ids}

    # 8. 获取收藏夹内容详情（按 content_type 分发查对应表）
    async def get_folder_contents(
        self, db: AsyncSession, user_id: int, folder_id: int,
        page: int = 1, page_size: int = 20
    ) -> dict:
        """把 content_ids 解析成具体内容返回"""
        folder = await favorite_crud.get(db, folder_id=folder_id, user_id=user_id)
        if not folder:
            raise CustomAPIException(code=ErrorCode.NOT_FOUND, message="收藏夹不存在")

        content_ids = folder.content_ids or []
        total = len(content_ids)
        start = (page - 1) * page_size
        end = start + page_size
        page_ids = content_ids[start:end]

        # 按 content_type 分发到不同业务表
        if not page_ids:
            items = []
        elif folder.content_type == "question":
            from crud.bank_questions_crud import get_bank_questions_by_ids
            items = await get_bank_questions_by_ids(db, ids=page_ids)
            items = [q.model_dump() for q in items]
        elif folder.content_type == "summary":
            from crud.messages_crud import msg_crud
            items = await msg_crud.get_by_ids(db, ids=page_ids)
            items = [m.model_dump() for m in items]
        else:
            # knowledge 或其他类型暂不支持
            items = []

        return {
            "folder": folder,
            "contents": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    

    # ==================== 管理端方法 ====================

    # 管理端：全量分页查询收藏夹
    async def get_folders_admin(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20,
        content_type: Optional[str] = None, user_id: Optional[int] = None
    ):
        skip = (page - 1) * page_size
        total = await favorite_crud.count_admin(
            db, content_type=content_type, user_id=user_id
        )
        items = await favorite_crud.get_multi_admin(
            db, skip=skip, limit=page_size,
            content_type=content_type, user_id=user_id
        )
        return PageResult(
            list=items,
            total=total,
            page=page,
            page_size=page_size
        )

    # 7. 管理端：获取单个收藏夹详情
    async def get_folder_admin(self, db: AsyncSession, folder_id: int):
        folder = await favorite_crud.get(db, folder_id=folder_id)
        if not folder:
            raise CustomAPIException(
                code=ErrorCode.NOT_FOUND,
                message="收藏夹不存在"
            )
        return folder

        # 8. 管理端：批量删除收藏夹
    async def batch_delete_admin(self, db: AsyncSession, ids: List[int]) -> int:
        try:
            if not ids:
                return 0
            count = await favorite_crud.delete_by_ids_admin(db, ids=ids)
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise CustomAPIException(
                code=ErrorCode.DB_OPERATION_FAILED,
                message=str(e)
            )

    # 9. 管理端：收藏夹热度排行
    async def get_top_favorites(
        self, db: AsyncSession, limit: int = 10, content_type: Optional[str] = None
    ):
        raw_list = await favorite_crud.get_top_favorites(db, limit=limit, content_type=content_type)
        result = []
        for row in raw_list:
            result.append({
                "folder_id": row.id,
                "content_type": row.content_type,
                "content_count": row.content_count
            })
        return result


fav_service = FavoriteService()