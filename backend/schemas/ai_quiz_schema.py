# schemas/ai_quiz_schema.py
from fastapi import Form
from typing import Optional, List
import json

class QuizGenerateFormDependency:
    def __init__(
        self,
        session_id: int = Form(1, description="当前的会话ID"),
        bank_name: str = Form("《书途》智能测试题", description="生成的题库名称"),
        model_name: Optional[str] = Form("deepseek-ai/DeepSeek-V3", description="指定调用的大模型"),
        content: Optional[str] = Form("请根据李白的《静夜思》出几道题", description="纯文本内容"),
        
        attachment_ids: str = Form("[]", description="已上传附件的ID列表(JSON数组字符串)，例如: [1, 2, 3]"),
        
        question_count: int = Form(5, description="需要生成的总题数", ge=1, le=20),
        difficulty: str = Form("medium", description="难度：easy/medium/hard"),
        question_types: str = Form(
            "single_choice,multi_choice,essay", 
            description="需要的题型（逗号分隔）"
        ),
        target_bank_id: Optional[int] = Form(None, description="追加模式：传入已有的题库ID；不传则新建题库")
    ):
        self.session_id = session_id
        self.bank_name = bank_name
        self.model_name = model_name
        self.content = content
        self.question_count = question_count
        self.difficulty = difficulty
        self.question_types = question_types
        self.target_bank_id = target_bank_id
        
        # 将前端传来的 JSON 字符串数组解析为 List[int]
        try:
            self.attachment_ids = json.loads(attachment_ids)
        except Exception:
            self.attachment_ids = []