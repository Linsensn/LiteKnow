from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# 请求：单条新增题库
class QuestionBankCreate(BaseModel):
    bank_name: str = Field(..., description="题库名称")
    description: Optional[str] = Field(None, description="题库描述")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_name": "操作系统原理期末复习题库",
                "description": "包含进程管理、内存分配、文件系统等核心考点"
            }
        }
    )

# 请求：单条/批量更新题库（字段均可选）
class QuestionBankUpdate(BaseModel):
    bank_name: Optional[str] = Field(None, description="题库名称")
    description: Optional[str] = Field(None, description="题库描述")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_name": "操作系统原理期末复习题库 (2026版)",
                "description": "更新了最新考纲要求的并发控制题目"
            }
        }
    )

# 请求：批量更新包裹
class BatchUpdateBankReq(BaseModel):
    ids: List[int] = Field(..., description="需要更新的题库ID列表")
    update_data: QuestionBankUpdate = Field(..., description="统一更新的数据源")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [2001, 2002],
                "update_data": {
                    "description": "已归档题库"
                }
            }
        }
    )

# 请求：批量删除
class BulkDeleteIn(BaseModel):
    bank_ids: List[int] = Field(..., description="要操作的题库ID列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bank_ids": [2001, 2002, 2003]
            }
        }
    )

# 响应：单条题库信息输出 (已新增统计字段)
class QuestionBankOut(BaseModel):
    id: int
    user_id: int
    bank_name: str
    description: Optional[str]
    total_questions: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    # 动态统计字段
    completion_rate: Optional[float] = Field(0.0, description="完成率 (0-100的百分比数值)")
    accuracy_rate: Optional[float] = Field(0.0, description="正确率 (0-100的百分比数值)")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2001,
                "user_id": 8848,
                "bank_name": "操作系统原理期末复习题库",
                "description": "包含进程管理、内存分配、文件系统等核心考点",
                "total_questions": 150,
                "completion_rate": 0.0,
                "accuracy_rate": 0.0,
                "created_at": "2026-07-01T10:00:00",
                "updated_at": "2026-07-05T20:00:00"
            }
        }
    )