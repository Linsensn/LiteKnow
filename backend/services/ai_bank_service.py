# backend/services/ai_bank_service.py
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException

# 引入统一大模型客户端
from utils.llm_client import llm_client 
from schemas.ai_bank_schema import BankParseRequest, ParsedQuestion, BankParseResponse

logger = logging.getLogger("liteknow.ai_bank")

class AIBankService:
    def __init__(self):
        # 【重要修改】：提示词全面适配新的数据库规范
        self.system_prompt = (
            "你是一个专业的教育内容处理助手。"
            "用户会输入一段杂乱的包含练习题的纯文本，请仔细分析并提取出所有的题目，"
            "整理成规范的JSON格式返回。"
            "要求返回的JSON对象必须包含一个名为 'questions' 的数组，"
            "数组中每个元素包含以下字段："
            "- question_type: 题型（必须是 single_choice, multi_choice, essay 或 application）\n"
            "- difficulty_level: 难度评估（easy, medium 或 hard，默认为 medium）\n"
            "- content: 题干内容\n"
            "- options: 选项数组。必须是对象数组，规范为：[{\"id\": \"A\", \"content\": \"选项1\"}, {\"id\": \"B\", \"content\": \"选项2\"}]。如果是简答题/应用题等无选项题目，请留空数组 []\n"
            "- correct_answer: 正确答案。必须以JSON支持的格式返回！(例如：单选题请返回 [\"B\"]，多选题返回 [\"A\", \"C\"]，简答题返回文本字符串)\n"
            "- ai_analysis: 题目解析（如果原文没有，请结合你的知识给出简要解析）\n"
            "请确保严格输出合法的JSON格式。"
        )

    async def parse_and_save_bank(
        self, db: AsyncSession, user_id: int, req: BankParseRequest
    ) -> BankParseResponse:
        try:
            llm_response_str = await llm_client.async_call_llm(
                system_prompt=self.system_prompt,
                user_prompt=req.content,
                response_format="json_object"
            )

            try:
                llm_data = json.loads(llm_response_str)
                questions_data = llm_data.get("questions", [])
            except json.JSONDecodeError:
                logger.error(f"大模型返回的不是有效的JSON: {llm_response_str}")
                raise HTTPException(status_code=500, detail="大模型返回格式解析失败")

            if not questions_data:
                raise HTTPException(status_code=400, detail="未能从文本中识别出任何题目。")

            # 插入题库表
            bank_insert_sql = text('''
                INSERT INTO question_banks (user_id, bank_name, description, total_questions, created_at, updated_at) 
                VALUES (:user_id, :bank_name, :description, :total_questions, NOW(), NOW())
            ''')
            result = await db.execute(bank_insert_sql, {
                "user_id": user_id,
                "bank_name": req.bank_name,
                "description": "由大模型自动识别生成的题库",
                "total_questions": len(questions_data)
            })
            bank_id = result.lastrowid
            
            parsed_questions = []
            
            # 【重要修改】：SQL插入包含 difficulty_level，并将 correct_answer 转换为 JSON 序列化存储
            question_insert_sql = text('''
                INSERT INTO bank_questions 
                (bank_id, question_type, difficulty_level, content, options_json, correct_answer, ai_analysis, created_at, updated_at) 
                VALUES (:bank_id, :question_type, :difficulty_level, :content, :options_json, :correct_answer, :ai_analysis, NOW(), NOW())
            ''')

            for q in questions_data:
                parsed_q = ParsedQuestion(
                    question_type=q.get("question_type", "single_choice"),
                    difficulty_level=q.get("difficulty_level", "medium"),
                    content=q.get("content", ""),
                    options=q.get("options", []),
                    correct_answer=q.get("correct_answer", []),
                    ai_analysis=q.get("ai_analysis", "")
                )
                parsed_questions.append(parsed_q)

                # 使用 Pydantic 的 model_dump 转字典后进行 JSON 序列化
                options_to_save = [opt.model_dump() for opt in parsed_q.options] if parsed_q.options else []

                await db.execute(question_insert_sql, {
                    "bank_id": bank_id,
                    "question_type": parsed_q.question_type,
                    "difficulty_level": parsed_q.difficulty_level,
                    "content": parsed_q.content,
                    "options_json": json.dumps(options_to_save, ensure_ascii=False),
                    "correct_answer": json.dumps(parsed_q.correct_answer, ensure_ascii=False),
                    "ai_analysis": parsed_q.ai_analysis
                })
            
            await db.commit()

            return BankParseResponse(
                bank_id=bank_id,
                bank_name=req.bank_name,
                total_questions=len(parsed_questions),
                questions=parsed_questions
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"题库解析并落库失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"题库处理失败: {str(e)}")

ai_bank_service = AIBankService()