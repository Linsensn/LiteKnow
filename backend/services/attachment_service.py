# backend/services/attachment_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from utils.exceptions import CustomAPIException, ErrorCode
from crud.attachments_crud import attachment_crud
from schemas.attachment_schema import AttachmentResponse
from schemas.common import PageResult

class AttachmentService:

    # 1. 获取单条附件详情
    async def get_attachment(self, db: AsyncSession, attachment_id: int):
        attachment = await attachment_crud.get(db, attachment_id=attachment_id)
        if not attachment:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND)
        return attachment

    # 2. 分页获取附件列表（通用，通过 user_id 控制权限范围）
    async def get_attachment_page(
        self, db: AsyncSession, *, user_id: int = None,
        file_type: str = None, page: int, page_size: int
    ):
        skip = (page - 1) * page_size
        total = await attachment_crud.count(
            db, user_id=user_id, file_type=file_type
        )
        items = await attachment_crud.get_multi(
            db, user_id=user_id, file_type=file_type,
            skip=skip, limit=page_size
        )
        return PageResult(
            list=items,
            total=total,
            page=page,
            page_size=page_size
        )

    # 3. 创建附件记录
    async def create_attachment(
        self, db: AsyncSession, *, user_id: int, file_type: str,
        file_url: str, extracted_text: str = None, message_id: int = None
    ):
        try:
            new_attachment = await attachment_crud.create_with_owner(
                db, user_id=user_id, file_type=file_type,
                file_url=file_url, extracted_text=extracted_text,
                message_id=message_id
            )
            await db.commit()
            await db.refresh(new_attachment)
            return new_attachment
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)

    # 4. 删除附件（学生端需校验归属权）
    async def delete_attachment(
        self, db: AsyncSession, *, attachment_id: int, user_id: int = None
    ):
        attachment = await self.get_attachment(db, attachment_id=attachment_id)
        
        # 学生端校验归属，管理员端跳过
        if user_id is not None and attachment.user_id != user_id:
            raise CustomAPIException(code=ErrorCode.RESOURCE_ACCESS_DENIED)

        try:
            await attachment_crud.delete(db, db_obj=attachment)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED)


att_service = AttachmentService()