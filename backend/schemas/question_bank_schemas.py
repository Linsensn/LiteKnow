from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# 请求：单条新增题库
class QuestionBankCreate(BaseModel):
    bank_name: str = Field(..., description="题库名称")
    description: Optional[str] = Field(None, description="题库描述")

# 请求：单条/批量更新题库（字段均可选）
class QuestionBankUpdate(BaseModel):
    bank_name: Optional[str] = Field(None, description="题库名称")
    description: Optional[str] = Field(None, description="题库描述")

# 请求：批量更新包裹
class BatchUpdateBankReq(BaseModel):
    ids: List[int] = Field(..., description="需要更新的题库ID列表")
    update_data: QuestionBankUpdate = Field(..., description="统一更新的数据源")

# 请求：批量删除
class BulkDeleteIn(BaseModel):
    bank_ids: List[int] = Field(..., description="要操作的题库ID列表")

# 响应：单条题库信息输出
class QuestionBankOut(BaseModel):
    id: int
    user_id: int
    bank_name: str
    description: Optional[str]
    total_questions: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)