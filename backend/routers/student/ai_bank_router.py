# backend/routers/student/ai_bank_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session # 🌟 修改：从 asyncio 换成了 orm 同步引入

from config.database import get_db
from utils.deps import get_current_user
from utils.response import success  
from schemas.ai_bank_schema import BankParseRequest, BankParseResponse
from services.ai_bank_service import ai_bank_service

router = APIRouter(prefix="/ai/bank", tags=["Student/AI/智能题库"])

@router.post("/parse", response_model=BankParseResponse, summary="提取文本生成结构化题库")
async def parse_text_to_bank(
    req: BankParseRequest,
    db: Session = Depends(get_db), # 🌟 修改：类型提示改为 Session
    current_student = Depends(get_current_user)
):
    user_id = current_student.id
    
    # 获取 Service 返回的 JSON 结构并直接响应
    data = await ai_bank_service.parse_and_save_bank(
        db=db, user_id=user_id, req=req
    )
    return success(data=data)  
