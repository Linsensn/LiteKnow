# backend/services/ai_bank_service.py
import json
import logging
import re
from sqlalchemy.orm import Session # 🌟 修改：改为引入同步的 Session
from sqlalchemy import text
from fastapi import HTTPException

# 引入统一大模型客户端
from utils.llm_client import llm_client 
from schemas.ai_bank_schema import BankParseRequest, ParsedQuestion, BankParseResponse

logger = logging.getLogger("liteknow.ai_bank")

class AIBankService:
    def __init__(self):
        self.system_prompt = (
            "你是一个专业的教育内容处理助手。"
            "用户会输入一段杂乱的包含练习题的纯文本，请仔细分析并提取出所有的题目，"
            "整理成规范的JSON格式返回。\n"
            "【注意】：你只需要返回JSON数据，不要包含任何额外的解释说明，也不要使用 ```json 这样的代码块包裹！\n"
            "要求返回的JSON对象必须包含一个名为 'questions' 的数组，"
            "数组中每个元素包含以下字段："
            "- question_type: 题型（必须是 single_choice, multi_choice, essay 或 application）\n"
            "- difficulty_level: 难度评估（easy, medium 或 hard，默认为 medium）\n"
            "- content: 题干内容\n"
            "- options: 选项数组。必须是对象数组，规范为：[{\"id\": \"A\", \"content\": \"选项1\"}, {\"id\": \"B\", \"content\": \"选项2\"}]。如果是简答题/应用题等无选项题目，请留空数组 []\n"
            "- correct_answer: 正确答案。必须以JSON支持的格式返回！(例如：单选题请返回 [\"B\"]，多选题返回 [\"A\", \"C\"]，简答题返回文本字符串)\n"
            "- ai_analysis: 题目解析（如果原文没有，请结合你的知识给出简要解析）\n"
        )

    async def parse_and_save_bank(
        self, db: Session, user_id: int, req: BankParseRequest  # 🌟 修改：入参改为同步 Session
    ) -> BankParseResponse:
        try:
            logger.info(f"==> 开始处理题库解析任务，用户ID: {user_id}")
            logger.info("==> 正在请求大模型 (非流式)... 请耐心等待！")

            # 调用大模型 (LLM网络请求依然是异步的，保留 await)
            llm_response_str = await llm_client.async_call_llm(
                system_prompt=self.system_prompt,
                user_prompt=req.content,
                response_format="text"
            )
            
            logger.info(f"==> 大模型响应成功！返回数据前 100 个字符: {llm_response_str[:100]}...")

            # 防御性清洗机制
            cleaned_response = llm_response_str.strip()
            json_match = re.search(r'```json\s*(.*?)\s*```', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(1)
            else:
                json_match = re.search(r'```\s*(.*?)\s*```', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(1)

            try:
                llm_data = json.loads(cleaned_response)
                
                # 🌟 修改：智能判断 LLM 吐出的是数组还是字典，双重保险！
                if isinstance(llm_data, list):
                    questions_data = llm_data
                elif isinstance(llm_data, dict):
                    questions_data = llm_data.get("questions", [])
                else:
                    questions_data = []
                    
            except json.JSONDecodeError:
                logger.error(f"大模型返回的依然不是有效的JSON: {cleaned_response}")
                raise HTTPException(status_code=500, detail="大模型返回格式解析失败，请检查模型输出")

            if not questions_data:
                raise HTTPException(status_code=400, detail="未能从文本中识别出任何题目。")

            logger.info(f"==> 成功解析出 {len(questions_data)} 道题目，准备写入数据库...")

            # 🌟 修改：以下所有 db 操作全部去掉 await，适配同步环境
            bank_insert_sql = text('''
                INSERT INTO question_banks (user_id, bank_name, description, total_questions, created_at, updated_at) 
                VALUES (:user_id, :bank_name, :description, :total_questions, NOW(), NOW())
            ''')
            result = db.execute(bank_insert_sql, {
                "user_id": user_id,
                "bank_name": req.bank_name,
                "description": "由大模型自动识别生成的题库",
                "total_questions": len(questions_data)
            })
            bank_id = result.lastrowid
            
            parsed_questions = []
            
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

                options_to_save = [opt.model_dump() for opt in parsed_q.options] if parsed_q.options else []

                db.execute(question_insert_sql, {
                    "bank_id": bank_id,
                    "question_type": parsed_q.question_type,
                    "difficulty_level": parsed_q.difficulty_level,
                    "content": parsed_q.content,
                    "options_json": json.dumps(options_to_save, ensure_ascii=False),
                    "correct_answer": json.dumps(parsed_q.correct_answer, ensure_ascii=False),
                    "ai_analysis": parsed_q.ai_analysis
                })
            
            db.commit() # 🌟 修改：去掉 await
            logger.info(f"==> 题库落库成功！Bank ID: {bank_id}。任务彻底完成！")

            return BankParseResponse(
                bank_id=bank_id,
                bank_name=req.bank_name,
                total_questions=len(parsed_questions),
                questions=parsed_questions
            )

        except HTTPException:
            raise
        except Exception as e:
            db.rollback() # 🌟 修改：去掉 await，彻底解决 TypeError
            logger.error(f"题库解析并落库失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"题库处理失败: {str(e)}")

ai_bank_service = AIBankService()