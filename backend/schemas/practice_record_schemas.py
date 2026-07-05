from pydantic import BaseModel, ConfigDict, Field

# 请求：提交单道题的作答
class PracticeRecordSubmit(BaseModel):
    session_id: int = Field(..., description="当前关联的练习会话ID")
    question_id: int = Field(..., description="答题的题目ID")
    user_answer: str = Field(..., description="用户的选项或文本回答")
    correct_answer: str = Field(..., description="正确答案比对标识")
    question_content: str = Field(..., description="题干快照，用于错题本冗余展示")
    current_index: int = Field(..., description="该题目在序列中的位置索引，用于记录进度")

# 响应：提交结果反馈
class SubmitResultOut(BaseModel):
    is_correct: bool