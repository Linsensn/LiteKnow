from pydantic import BaseModel, Field

class QuizGenerateRequest(BaseModel):
    session_id: int = Field(..., description="当前的会话ID")
    content: str = Field(..., description="要生成测验的课本内容/要点")
    bank_name: str = Field(default="AI智能测验题库", description="生成的题库名称")