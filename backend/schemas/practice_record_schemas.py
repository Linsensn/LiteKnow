from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any
from datetime import datetime

# 请求：提交单道题的作答 (保持原有业务)
class PracticeRecordSubmit(BaseModel):
    session_id: int = Field(..., description="当前关联的练习会话ID")
    question_id: int = Field(..., description="答题的题目ID")
    user_answer: Any = Field(..., description="用户实际作答内容(JSON格式)")
    correct_answer: Any = Field(..., description="正确答案(JSON格式)")
    question_content: str = Field(..., description="题干快照，用于错题本冗余展示")
    current_index: int = Field(..., description="该题目在序列中的位置索引，用于记录进度")
    option_sequence: Optional[List[str]] = Field(default=None, description="(选项乱序时使用)展示的选项ID顺序，未打乱则为空")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 1024,
                "question_id": 5050,
                "user_answer": ["B"],  # 变更为JSON数组或对象示例
                "correct_answer": ["C"],
                "question_content": "TCP协议的三次握手中，第二次握手发送的标志位是？",
                "current_index": 5,
                "option_sequence": ["C", "A", "D", "B"]
            }
        }
    )

# 请求：单条新增
class PracticeRecordCreate(BaseModel):
    session_id: int = Field(..., description="练习会话ID")
    question_id: int = Field(..., description="题目ID")
    is_completed: bool = Field(default=False, description="是否已作答")
    is_correct: Optional[bool] = Field(default=None, description="是否正确(简答题可扩展支持小数得分)")
    user_answer: Optional[Any] = Field(default=None, description="用户作答内容(JSON格式)")
    option_sequence: Optional[List[str]] = Field(default=None, description="(选项乱序时使用)展示的选项ID顺序")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 1024,
                "question_id": 5050,
                "is_completed": True,
                "is_correct": False,
                "user_answer": ["B"],
                "option_sequence": ["C", "A", "D", "B"]
            }
        }
    )

# 请求：单条/批量更改
class PracticeRecordUpdate(BaseModel):
    is_completed: Optional[bool] = None
    is_correct: Optional[bool] = None
    user_answer: Optional[Any] = None
    option_sequence: Optional[List[str]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_completed": True,
                "is_correct": True,
                "user_answer": ["C"],
                "option_sequence": ["C", "A", "D", "B"]
            }
        }
    )

# 请求：批量更新包裹
class BatchUpdateReq(BaseModel):
    ids: List[int] = Field(..., description="需要更新的记录ID列表")
    update_data: PracticeRecordUpdate = Field(..., description="统一更新的数据源")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [101, 102, 103],
                "update_data": {
                    "is_completed": True,
                    "is_correct": True,
                    "user_answer": ["A"],
                    "option_sequence": ["A", "B", "C", "D"]
                }
            }
        }
    )

# 请求：批量删除
class BatchDeleteReq(BaseModel):
    ids: List[int] = Field(..., description="需要删除的记录ID列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [101, 102, 103]
            }
        }
    )

# 请求：状态切换
class StatusToggleReq(BaseModel):
    is_correct: bool = Field(..., description="更新后的正误状态")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_correct": True
            }
        }
    )

# 响应：提交结果反馈
class SubmitResultOut(BaseModel):
    is_correct: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_correct": False
            }
        }
    )

# 响应：单条答题记录详情
class PracticeRecordDetailOut(BaseModel):
    id: int
    session_id: int
    question_id: int
    is_completed: Optional[bool]
    is_correct: Optional[bool]
    user_answer: Optional[Any]
    option_sequence: Optional[List[str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 9527,
                "session_id": 1024,
                "question_id": 5050,
                "is_completed": True,
                "is_correct": False,
                "user_answer": ["B"],
                "option_sequence": ["C", "A", "D", "B"],
                "created_at": "2026-07-05T21:30:00",
                "updated_at": "2026-07-05T21:35:00"
            }
        }
    )