# backend/routers/student/ai_bank_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 依赖注入组件对齐组长的导入
from config.database import get_db
from utils.deps import get_current_user

from schemas.ai_bank_schema import BankParseRequest, BankParseResponse
from services.ai_bank_service import ai_bank_service

router = APIRouter(prefix="/ai/bank", tags=["Student/AI/智能题库"])

@router.post("/parse", response_model=BankParseResponse, summary="提取文本生成结构化题库")
async def parse_text_to_bank(
    req: BankParseRequest,
    db: AsyncSession = Depends(get_db),
    current_student: dict = Depends(get_current_user)
):
    """
    处理纯文本格式的题库解析请求。
    调用大模型提取并归一化题目结构，持久化后返回给小程序用于练习渲染。
    """
    # 假设 get_current_user 提供了包含 id 的字典
    user_id = current_student.get("id")
    
    # 获取 Service 返回的 JSON 结构并直接响应
    return await ai_bank_service.parse_and_save_bank(
        db=db, 
        user_id=user_id, 
        req=req
    )