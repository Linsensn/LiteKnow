from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# 请求：单条/批量外部导入错题
class WrongQuestionImport(BaseModel):
    question_id: Optional[int] = Field(None, description="关联的题库原题ID")
    question_content: str = Field(..., description="题目完整文本")
    source_image_url: Optional[str] = Field(None, description="原始拍照图片链接")
    user_answer: Optional[str] = Field(None, description="用户错误答案")
    correct_answer: Optional[str] = Field(None, description="正确答案")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question_content": "以下哪个不是进程调度的算法？ A. FCFS  B. LRU  C. RR  D. SJF",
                "source_image_url": "https://oss.example.com/images/wrong_q_123.jpg",
                "user_answer": "D",
                "correct_answer": "B"
            }
        }
    )

# 请求：通用更新（含个人解析）
class WrongQuestionUpdate(BaseModel):
    question_content: Optional[str] = None
    my_analysis: Optional[str] = Field(None, description="学生自己撰写的反思与解析")
    user_answer: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "my_analysis": "看错题了，LRU是页面置换算法，不是进程调度算法，下次要注意审题区分概念。",
                "user_answer": "D"
            }
        }
    )

# 请求：批量更新包裹
class BatchUpdateWrongQuestionsReq(BaseModel):
    ids: List[int] = Field(..., description="需要更新的错题ID列表")
    update_data: WrongQuestionUpdate = Field(..., description="统一更新的数据")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [3001, 3002],
                "update_data": {
                    "my_analysis": "复习时需重点回顾这部分的理论基础。"
                }
            }
        }
    )

# 请求：批量删除错题
class BatchDeleteWrongQuestionsReq(BaseModel):
    ids: List[int] = Field(..., description="需要移出错题本的ID列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [3001, 3002, 3003]
            }
        }
    )

# 响应：错题本单条记录
class WrongQuestionOut(BaseModel):
    id: int
    user_id: int
    question_id: Optional[int] = Field(None, description="关联的原题ID，可跳转追溯")
    question_content: str
    source_image_url: Optional[str]
    user_answer: Optional[str]
    correct_answer: Optional[str]
    ai_analysis: Optional[str]
    my_analysis: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 3001,
                "user_id": 8848,
                "question_content": "以下哪个不是进程调度的算法？ A. FCFS  B. LRU  C. RR  D. SJF",
                "source_image_url": "https://oss.example.com/images/wrong_q_123.jpg",
                "user_answer": "D",
                "correct_answer": "B",
                "ai_analysis": "AI解析：LRU（最近最少使用）是内存管理中常用的页面置换算法。FCFS、RR、SJF均属于进程调度算法。",
                "my_analysis": "看错题了，LRU是页面置换算法，下次要注意审题区分概念。",
                "created_at": "2026-07-05T21:40:00",
                "updated_at": "2026-07-05T21:45:00"
            }
        }
    )