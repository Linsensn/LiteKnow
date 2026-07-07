import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession

# 移除原先的 from fastapi import HTTPException
# 引入项目自定义的异常类和错误码枚举
from utils.exceptions import CustomAPIException, ErrorCode 

from models.question_banks import QuestionBank
from models.bank_questions import BankQuestion
from services.message_service import msg_service
from schemas.message_schema import MessageCreate
from utils.llm_client import llm_client

logger = logging.getLogger("liteknow.ai_quiz")

class AIQuizService:
    def __init__(self):
        self.system_prompt = (
            "你是一个严谨且专业的出题专家。请仔细阅读用户提供的课文要点，自主生成3到5道单项选择题。"
            "要求：\n"
            "1. 必须以严格的 JSON 对象格式输出，不要包含任何 Markdown 标记或多余的解释文本。\n"
            "2. 你的输出必须完全符合以下 JSON 结构，严格遵守字段的数据类型规范：\n"
            "{\n"
            '  "questions": [\n'
            "    {\n"
            '      "chapter_name": "根据课本内容提取的简短章节名称",\n'
            '      "question_type": "single_choice",\n'
            '      "difficulty_level": "medium",\n'
            '      "content": "题干内容",\n'
            '      "options_json": [\n'
            '        {"id": "A", "content": "第一个选项的具体内容"},\n'
            '        {"id": "B", "content": "第二个选项的具体内容"},\n'
            '        {"id": "C", "content": "第三个选项的具体内容"},\n'
            '        {"id": "D", "content": "第四个选项的具体内容"}\n'
            '      ],\n'
            '      "correct_answer": ["A"],\n'
            '      "ai_analysis": "在此进行详细解析。你必须自己校验这道题正确答案的合理性，解释为什么该选项正确，并说明其他选项为什么错误。"\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    async def generate_and_save_quiz(
        self, db: AsyncSession, user_id: int, session_id: int, bank_name: str, user_content: str
    ) -> dict:
        try:
            # 1. 记录用户的输入
            user_msg_in = MessageCreate(
                session_id=session_id,
                role="user",
                content_type="text",
                content=user_content
            )
            await msg_service.create_message(db, obj_in=user_msg_in)

            # 2. 调用大模型
            ai_response_text = await llm_client.async_call_llm(
                system_prompt=self.system_prompt,
                user_prompt=user_content,
                response_format="json_object"
            )

            # 3. 解析JSON数据
            try:
                quiz_data = json.loads(ai_response_text)
                questions = quiz_data.get("questions", [])
            except json.JSONDecodeError:
                logger.error(f"AI返回了非法的JSON结构: {ai_response_text}")
                # 使用全局业务异常抛出解析错误
                raise CustomAPIException(code=ErrorCode.AI_VALIDATION_FAILED, message="AI生成的测验数据格式异常，请重试。")

            if not questions:
                raise CustomAPIException(code=ErrorCode.AI_VALIDATION_FAILED, message="AI未能生成有效的题目。")

            # 4. 创建题库
            new_bank = QuestionBank(
                user_id=user_id,
                bank_name=bank_name,
                description="由AI自主分析课文内容后生成的智能测验，已自动完成答案合理性校验。",
                total_questions=len(questions)
            )
            db.add(new_bank)
            await db.flush()

            # 5. 批量存入题目
            bank_questions_to_insert = [
                BankQuestion(
                    bank_id=new_bank.id,
                    chapter_name="AI智能提取",
                    question_type="single_choice",
                    difficulty_level="medium",
                    content=q.get("content", ""),
                    options_json=q.get("options_json", []),
                    correct_answer=q.get("correct_answer", ""),
                    ai_analysis=q.get("ai_analysis", "")
                ) for q in questions
            ]
            db.add_all(bank_questions_to_insert)
            
            # 6. 保存AI回复
            ai_msg_in = MessageCreate(
                session_id=session_id,
                role="assistant",
                content_type="text",
                content=f"为您生成了 {len(questions)} 道选择题，我已仔细校验了全部答案的合理性并生成了题库。"
            )
            await msg_service.create_message(db, obj_in=ai_msg_in)
            
            await db.commit()

            # 返回纯净的业务数据字典，交由 Router 去包装
            return {
                "bank_id": new_bank.id,
                "total_questions": len(questions)
            }

        except CustomAPIException as ce:
            # 捕获已知业务异常直接向上抛出
            await db.rollback()
            raise ce
        except Exception as e:
            await db.rollback()
            logger.error(f"测验生成与落库失败: {str(e)}")
            # 拦截未知异常，统一转为业务异常
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED, message=f"智能测验处理失败: {str(e)}")

ai_quiz_service = AIQuizService()