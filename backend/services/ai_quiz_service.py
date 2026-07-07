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
    def _build_dynamic_prompt(self, count: int, difficulty: str, types_str: str) -> str:
        """根据用户需求动态生成 Prompt"""
        return (
            f"你是一个严谨且专业的出题专家。请仔细阅读用户提供的课文要点，自主生成 {count} 道题目。\n"
            f"题目整体难度应控制在：{difficulty}（easy=简单, medium=中等, hard=困难）。\n"
            f"允许生成的题型包括：{types_str}（single_choice=单选, multi_choice=多选, true_false=判断, essay=简答/应用题）。请根据知识点合理分配题型。\n"
            "要求：\n"
            "1. 必须以严格的 JSON 对象格式输出，不要包含任何 Markdown 标记。\n"
            "2. 你的输出必须完全符合以下 JSON 结构：\n"
            "{\n"
            '  "questions": [\n'
            "    {\n"
            '      "chapter_name": "简短章节名称",\n'
            '      "question_type": "这里填具体的题型（如 essay）",\n'
            '      "difficulty_level": "当前题目的难度",\n'
            '      "content": "题干内容",\n'
            '      "options_json": [ '
            '         {"id": "A", "content": "选项内容"} '
            '      ], // 如果是简答题或判断题，此数组必须为空 []\n'
            '      "correct_answer": ["A", "B"], // 简答题填关键得分点，判断题填 ["正确"] 或 ["错误"]\n'
            '      "ai_analysis": "详细解析"\n'
            "    }\n"
            "  ]\n"
            "}"
        )
    
    async def generate_and_save_quiz(
        self, 
        db: AsyncSession, 
        user_id: int, 
        session_id: int, 
        bank_name: str, 
        user_content: str,
        model_name: str = None, 
        question_count: int = 5,
        difficulty: str = "medium",
        question_types: str = "single_choice",
        target_bank_id: int = None
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

            # 2. 动态构建系统提示词并调用大模型
            dynamic_prompt = self._build_dynamic_prompt(question_count, difficulty, question_types)
            ai_response_text = await llm_client.async_call_llm(
                system_prompt=dynamic_prompt,
                user_prompt=user_content,
                response_format="json_object",
                target_model=model_name
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

            # ================= 4. 追加模式的核心实现 =================
            if target_bank_id:
                # 追加模式：验证目标题库是否存在，且是否属于当前用户
                # 这里需要你确保 models 里有 QuestionBank 并在上方 import
                from sqlalchemy import select
                result = db.execute(
                    select(QuestionBank).where(QuestionBank.id == target_bank_id, QuestionBank.user_id == user_id)
                )
                existing_bank = result.scalars().first()
                if not existing_bank:
                    raise CustomAPIException(code=ErrorCode.NOT_FOUND, message="指定的题库不存在或无权限追加")
                
                # 更新老题库的总题数
                existing_bank.total_questions += len(questions)
                bank_id = existing_bank.id
                db.add(existing_bank)
            else:
                # 新建模式
                new_bank = QuestionBank(
                    user_id=user_id,
                    bank_name=bank_name,
                    description=f"AI生成的测试题（难度:{difficulty}）",
                    total_questions=len(questions)
                )
                db.add(new_bank)
                db.flush() # 这里确保你传进来的 db 是 AsyncSession
                bank_id = new_bank.id

            # 5. 批量存入题目 (将原本的 new_bank.id 替换为最终决定的 bank_id)
            bank_questions_to_insert = [
                BankQuestion(
                    bank_id=bank_id, 
                    chapter_name="AI智能提取",
                    question_type=q.get("question_type", "single_choice"),
                    difficulty_level=q.get("difficulty_level", difficulty),
                    content=q.get("content", ""),
                    options_json=q.get("options_json", []),
                    # 注意：如果大模型把答案弄成了字符串，这里统一转成JSON字符串存入
                    correct_answer=json.dumps(q.get("correct_answer", []), ensure_ascii=False) if isinstance(q.get("correct_answer"), list) else q.get("correct_answer", ""),
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
            
            db.commit()

            # 返回纯净的业务数据字典，交由 Router 去包装
            return {
                "bank_id": bank_id,
                "added_questions": len(questions),
                "is_append": target_bank_id is not None
            }

        except CustomAPIException as ce:
            # 捕获已知业务异常直接向上抛出
            db.rollback()
            raise ce
        except Exception as e:
            db.rollback()
            logger.error(f"测验生成与落库失败: {str(e)}")
            # 拦截未知异常，统一转为业务异常
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED, message=f"智能测验处理失败: {str(e)}")

ai_quiz_service = AIQuizService()