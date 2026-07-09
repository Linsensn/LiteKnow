# backend/services/attachment_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from utils.exceptions import CustomAPIException, ErrorCode
from crud.attachments_crud import attachment_crud
from schemas.attachment_schema import AttachmentResponse, AttachmentUpdate
from schemas.common import PageResult


class AttachmentService:

    # ==================== 查询 ====================

    async def get_attachment(self, db: AsyncSession, attachment_id: int):
        """单条查询"""
        attachment = await attachment_crud.get(db, attachment_id=attachment_id)
        if not attachment:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND)
        return attachment

    async def get_attachment_by_id(self, db: AsyncSession, att_id: int, user_id: int):
        """单条查询（带用户归属校验）"""
        attachment = await attachment_crud.get(db, attachment_id=att_id)
        if not attachment or attachment.user_id != user_id:
            return None
        return attachment

    async def get_attachment_page(
        self, db: AsyncSession, *, user_id: int = None,
        file_type: str = None, page: int, page_size: int
    ):
        """分页查询"""
        skip = (page - 1) * page_size
        items, total = await attachment_crud.get_multi_attachments(
            db, user_id=user_id, file_type=file_type, skip=skip, limit=page_size
        )
        return PageResult(
            list=items,
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_attachments_filter(
        self, db: AsyncSession, *, user_id: Optional[int] = None,
        file_type: Optional[str] = None, keyword: Optional[str] = None,
        page: int = 1, page_size: int = 20
    ):
        """多条件组合 + 模糊分页查询"""
        skip = (page - 1) * page_size
        items, total = await attachment_crud.get_multi_filter(
            db, user_id=user_id, file_type=file_type, keyword=keyword,
            skip=skip, limit=page_size
        )
        return PageResult(
            list=items,
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_attachment_statistics(self, db: AsyncSession, *, user_id: Optional[int] = None) -> dict:
        """聚合统计：按文件类型分组"""
        return await attachment_crud.get_statistics(db, user_id=user_id)

    # ==================== 新增 ====================

    async def create_attachment(
        self, db: AsyncSession, *, user_id: int, file_type: str,
        file_url: str, extracted_text: str = None, message_id: int = None
    ):
        """创建附件记录"""
        try:
            new_attachment = await attachment_crud.create_with_owner(
                db, user_id=user_id, file_type=file_type,
                file_url=file_url, extracted_text=extracted_text,
                message_id=message_id
            )
            db.commit()
            db.refresh(new_attachment)
            return new_attachment
        except Exception as e:
            db.rollback()
            print(f"！！！数据库插入失败的真正原因：{str(e)} ！！！")
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # ==================== 更新 ====================

    async def update_attachment(
        self, db: AsyncSession, attachment_id: int, update_data: AttachmentUpdate
    ):
        """编辑附件"""
        attachment = await self.get_attachment(db, attachment_id=attachment_id)
        try:
            updated = await attachment_crud.update_attachment(
                db, attachment_id=attachment_id,
                update_data=update_data.model_dump(exclude_none=True)
            )
            db.commit()
            return updated
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    async def batch_update_attachments(
        self, db: AsyncSession, ids: List[int], update_data: dict
    ) -> int:
        """批量更新附件"""
        try:
            count = await attachment_crud.update_by_ids(db, ids=ids, update_data=update_data)
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # ==================== 删除 ====================

    async def delete_attachment(
        self, db: AsyncSession, *, attachment_id: int, user_id: int = None
    ):
        """删除单条附件（学生端校验归属，管理端跳过）"""
        attachment = await self.get_attachment(db, attachment_id=attachment_id)
        if user_id is not None and attachment.user_id != user_id:
            raise CustomAPIException(code=ErrorCode.RESOURCE_ACCESS_DENIED)
        try:
            await attachment_crud.delete(db, db_obj=attachment)
            db.commit()
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    async def batch_delete_attachments(
        self, db: AsyncSession, ids: List[int], user_id: Optional[int] = None
    ) -> int:
        """批量删除（学生端带归属校验，管理端跳过）"""
        try:
            if user_id is not None:
                count = await attachment_crud.delete_by_ids(db, user_id=user_id, ids=ids)
            else:
                count = await attachment_crud.delete_by_ids_admin(db, ids=ids)
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # ==================== 导入导出 ====================

    async def export_attachments(self, db: AsyncSession, *, user_id: Optional[int] = None) -> List[dict]:
        """导出附件列表"""
        return await attachment_crud.export_attachments(db, user_id=user_id)

    async def import_attachments(self, db: AsyncSession, objs_in: List[dict]) -> int:
        """批量导入附件"""
        try:
            count = await attachment_crud.import_attachments(db, objs_in=objs_in)
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)


att_service = AttachmentService()