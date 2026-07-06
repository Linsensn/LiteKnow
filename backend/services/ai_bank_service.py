# backend/services/ai_bank_service.py
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException

# 引入组长封装好的统一大模型客户端
from utils.llm_client import llm_client 
from schemas.ai_bank_schema import BankParseRequest, ParsedQuestion, BankParseResponse

logger = logging.getLogger("liteknow.ai_bank")

class AIBankService:
    def __init__(self):
        # 提示词重点强调输出 JSON 格式
        self.system_prompt = (
            "你是一个专业的教育内容处理助手。"
            "用户会输入一段杂乱的包含练习题的纯文本，请你仔细分析并提取出所有的题目，"
            "整理成规范的JSON格式返回。"
            "要求返回的JSON对象必须包含一个名为 'questions' 的数组，"
            "数组中每个元素包含以下字段："
            "- question_type: 题型（必须是 single_choice, multi_choice 或 essay）\n"
            "- content: 题干内容\n"
            "- options: 选项数组（如果是选择题，提供完整的选项字符串列表，如果不是则为空数组[]）\n"
            "- correct_answer: 正确答案\n"
            "- ai_analysis: 题目解析（如果原文没有，请结合你的知识给出简要解析）\n"
            "请确保严格输出合法的JSON格式。"
        )

    async def parse_and_save_bank(
        self, db: AsyncSession, user_id: int, req: BankParseRequest
    ) -> BankParseResponse:
        try:
            # 1. 调用大模型非流式接口，要求强返回 JSON_OBJECT[cite: 2]
            llm_response_str = await llm_client.async_call_llm(
                system_prompt=self.system_prompt,
                user_prompt=req.content,
                response_format="json_object"
            )

            # 2. 解析大模型返回的 JSON
            try:
                llm_data = json.loads(llm_response_str)
                questions_data = llm_data.get("questions", [])
            except json.JSONDecodeError:
                logger.error(f"大模型返回的不是有效的JSON: {llm_response_str}")
                raise HTTPException(status_code=500, detail="大模型返回格式解析失败")

            if not questions_data:
                raise HTTPException(status_code=400, detail="未能从文本中识别出任何题目。")

            # 3. 数据落库
            # 3.1 插入 question_banks 表
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
            
            # 3.2 批量插入 bank_questions 表[cite: 5]
            question_insert_sql = text('''
                INSERT INTO bank_questions 
                (bank_id, question_type, content, options_json, correct_answer, ai_analysis, created_at, updated_at) 
                VALUES (:bank_id, :question_type, :content, :options_json, :correct_answer, :ai_analysis, NOW(), NOW())
            ''')

            for q in questions_data:
                # 序列化选项并构建 Pydantic 模型
                parsed_q = ParsedQuestion(
                    question_type=q.get("question_type", "single_choice"),
                    content=q.get("content", ""),
                    options=q.get("options", []),
                    correct_answer=q.get("correct_answer", ""),
                    ai_analysis=q.get("ai_analysis", "")
                )
                parsed_questions.append(parsed_q)

                await db.execute(question_insert_sql, {
                    "bank_id": bank_id,
                    "question_type": parsed_q.question_type,
                    "content": parsed_q.content,
                    "options_json": json.dumps(parsed_q.options, ensure_ascii=False),
                    "correct_answer": parsed_q.correct_answer,
                    "ai_analysis": parsed_q.ai_analysis
                })
            
            # 提交事务
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