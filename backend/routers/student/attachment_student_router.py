# backend/routers/student/attachments_student_route.py
from fastapi import APIRouter, Depends, Query, UploadFile, File, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from config.database import get_db
from utils.deps import get_current_user
from utils.response import success
from utils.exceptions import CustomAPIException, ErrorCode
from utils.local_storage import save_file_local
from utils.ocr_client import parse_local_file
from services.attachment_service import att_service
from schemas.common import ResponseModel, PageResult
from schemas.attachment_schema import AttachmentResponse

router = APIRouter(prefix="/attachments", tags=["Student - 资源管理"])

ALLOWED_TYPES = [
    "image/jpeg", 
    "image/png", 
    "application/pdf",
    "text/plain",           # .txt
    "text/markdown",        # .md
    "text/csv",             # .csv
    "application/msword",   # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # .docx
    "application/vnd.ms-excel", # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" # .xlsx
]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", summary="学生上传附件并自动解析", response_model=ResponseModel[AttachmentResponse])
async def upload_attachment(
    file: UploadFile = File(...),
    message_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    # 1. 校验文件类型
    if file.content_type not in ALLOWED_TYPES:
        raise CustomAPIException(code=ErrorCode.BUSINESS_PARAM_ERROR, message="不支持的文件类型")
    
    # 2. 读取并校验文件大小
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise CustomAPIException(code=ErrorCode.BUSINESS_PARAM_ERROR, message="文件大小不能超过10MB")
    
    # 3. 本地存储
    file_path = save_file_local(
        file_bytes=file_bytes,
        filename=file.filename,
        user_id=current_student.id
    )

    # 自动进行 OCR / 文本提取
    # 这一步就算解析失败（返回空字符串），也不阻断上传成功
    extracted_text = await parse_local_file(file_path, file.filename)
    
    # 4. 写入数据库，连同提取的文本一起保存
    new_attachment = await att_service.create_attachment(
        db=db,
        user_id=current_student.id,
        file_type=file.content_type,
        file_url=file_path,
        message_id=message_id,
        extracted_text=extracted_text 
    )
    
    # 5. 根据解析结果返回不同的提示语
    msg = "上传并解析成功" if extracted_text else "上传成功，但未识别到有效文字（可能是图片不清晰或为空白）"
    return success(data=AttachmentResponse.model_validate(new_attachment), message=msg)  # ← 改这行


@router.get("", summary="分页获取我的附件列表", response_model=ResponseModel[PageResult[AttachmentResponse]])
async def get_my_attachments(
    file_type: Optional[str] = Query(None, description="按类型筛选，如 image/jpeg"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    data = await att_service.get_attachment_page(
        db, user_id=current_student.id,
        file_type=file_type, page=page, page_size=page_size
    )
    data.list = [AttachmentResponse.model_validate(item) for item in data.list]  # ← 加这行
    return success(data=data)

@router.delete("/{attachment_id}", summary="删除我的附件")
async def delete_my_attachment(
    attachment_id: int = Path(..., description="附件ID"),
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    await att_service.delete_attachment(
        db, attachment_id=attachment_id, user_id=current_student.id
    )
    return success(message="附件删除成功")