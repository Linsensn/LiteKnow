from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from utils.deps import get_current_user
from utils.response import success 
from utils.exceptions import CustomAPIException,  ErrorCode
from utils.ocr_client import parse_file_content
from schemas.ai_quiz_schema import QuizGenerateFormDependency
from schemas.common import ResponseModel, PageResult
from services.ai_quiz_service import ai_quiz_service

router = APIRouter(prefix="/ai/quiz", tags=["Student/AI/智能测验"])

@router.post("/generate", summary="智能生成结构化测验", response_model=ResponseModel[dict])
async def create_smart_quiz(
    req: QuizGenerateFormDependency = Depends(), # 使用 Depends 注入表单类
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    # 1. 准备一个列表，用于收集所有的内容片段
    content_parts = []
    
    # 2. 如果用户在文本框输入了内容，先把它加进来
    if req.content and req.content.strip():
        content_parts.append(f"【用户补充说明】:\n{req.content.strip()}")

    # 3. 遍历处理所有上传的文件
    if req.files:
        for file in req.files:
            # 过滤掉空文件占位符（有时前端可能会传空的文件对象）
            if not file.filename:
                continue
                
            extracted_text = await parse_file_content(file)
            
            if extracted_text:
                # 加上文件名标识，能让大模型更好地理解上下文的分界线
                content_parts.append(f"【文件 {file.filename} 提取内容】:\n{extracted_text}")
            else:
                logger.warning(f"文件 {file.filename} 内容提取为空或解析失败")
                # 可选：如果你希望只要有一个文件解析失败就整体报错，可以在这里 raise 异常
                # raise CustomAPIException(code=ErrorCode.FILE_OR_IMAGE_VALIDATION_ERROR, message=f"文件 {file.filename} 解析失败")

    # 4. 最终校验：如果没有任何有效内容被提取出来，拦截请求
    if not content_parts:
        raise CustomAPIException(
            code=ErrorCode.FILE_OR_IMAGE_VALIDATION_ERROR, 
            message="请提供有效的文本内容或上传清晰的文件"
        )
        
    # 5. 将所有内容合并成一个长字符串
    final_user_content = "\n\n".join(content_parts)

    # 6. 交给底层 Service 处理
    result = await ai_quiz_service.generate_and_save_quiz(
        db=db,
        user_id=current_student["id"],
        session_id=req.session_id,
        bank_name=req.bank_name,
        user_content=final_user_content,
        model_name=req.model_name
    )
    
    return success(data=result, message="智能测验生成并入库成功")