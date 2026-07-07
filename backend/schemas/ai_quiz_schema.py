# schemas/ai_quiz_schema.py
from fastapi import Form, File, UploadFile
from typing import Optional, List

class QuizGenerateFormDependency:
    def __init__(
        self,
        session_id: int = Form(
            ..., 
            description="当前的会话ID", 
            example=1001
        ),
        bank_name: str = Form(
            "AI智能测验题库", 
            description="生成的题库名称", 
            example="《书途》YOLOv8识别算法测试题"
        ),
        model_name: Optional[str] = Form(
            None, 
            description="指定调用的大模型", 
            example="deepseek-ai/DeepSeek-V3"
        ),
        content: Optional[str] = Form(
            None, 
            description="纯文本内容", 
            example="YOLOv8 是一种先进的目标检测算法，在书脊检测和文本定位中表现优异。结合 PaddleOCR，系统可以实现端到端的书名提取与识别流程..."
        ),
        files: Optional[List[UploadFile]] = File(
            None, 
            description="图片或文档文件"
        )
    ):
        self.session_id = session_id
        self.bank_name = bank_name
        self.model_name = model_name
        self.content = content
        self.files = files