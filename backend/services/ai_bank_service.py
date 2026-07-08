# backend/services/ai_bank_service.py
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from utils.exceptions import CustomAPIException, ErrorCode
from utils.llm_client import llm_client 

# 🌟 新增：引入 LangChain 核心库
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

from schemas.ai_bank_schema import ParsedQuestion, BankParseResponse, BankParseOutputData

logger = logging.getLogger("liteknow.ai_bank")

class AIBankService:
    async def parse_and_save_bank(
        self, db: AsyncSession, user_id: int, bank_name: str, final_content: str
    ) -> BankParseResponse:
        
        logger.info(f"==> 开始处理题库解析任务，用户ID: {user_id}")
        logger.info("==> 正在使用 LangChain 请求大模型...")

        # 1. 初始化解析器（绑定我们的 BankParseOutputData）
        parser = PydanticOutputParser(pydantic_object=BankParseOutputData)
        
        # 2. 构建 Prompt 模板（注入格式要求）
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的教育内容处理助手。\n"
                       "请仔细分析用户提供的资料（包含杂乱的文字或OCR识别的题目记录），\n"
                       "提取出所有的题目，并整理成规范的格式返回。\n"
                       "如果原文附带解析，请提取到 ai_analysis 中；如果没有，请自主生成简要解析。\n\n"
                       "【重要格式要求】:\n{format_instructions}"),
            ("user", "资料素材：\n{final_content}")
        ]).partial(format_instructions=parser.get_format_instructions())

        # 3. 初始化大模型工具
        llm = llm_client.get_langchain_chat_model(temperature=0.2)
        
        # 4. 组装 LCEL 链
        chain = prompt | llm | parser

        # 5. 执行异步调用并自动解析为 Pydantic 对象
        try:
            # 这里的 bank_result 直接就是 BankParseOutputData 对象！
            bank_result: BankParseOutputData = await chain.ainvoke({
                "final_content": final_content
            })
            questions = bank_result.questions
        except OutputParserException as e:
            logger.error(f"LangChain 解析异常: {str(e)}")
            raise CustomAPIException(code=ErrorCode.AI_VALIDATION_FAILED, message="AI 提取失败，可能是内容过于杂乱，请重试。")
        except Exception as e:
            logger.error(f"LangChain 调用异常: {str(e)}")
            raise CustomAPIException(code=ErrorCode.AI_VALIDATION_FAILED, message=f"大模型响应失败: {str(e)}")

        if not questions:
            raise CustomAPIException(code=ErrorCode.AI_VALIDATION_FAILED, message="未能从素材中提取出任何题目。")

        logger.info(f"==> 成功解析出 {len(questions)} 道题目，准备落库...")

        try:
            # 6. 落库逻辑 (恢复 AsyncSession 操作)
            bank_insert_sql = text('''
                INSERT INTO question_banks (user_id, bank_name, description, total_questions, created_at, updated_at) 
                VALUES (:user_id, :bank_name, :description, :total_questions, NOW(), NOW())
            ''')
            result = db.execute(bank_insert_sql, {
                "user_id": user_id,
                "bank_name": bank_name,
                "description": "由大模型OCR智能提取的题库",
                "total_questions": len(questions)
            })
            bank_id = result.lastrowid
            
            question_insert_sql = text('''
                INSERT INTO bank_questions 
                (bank_id, question_type, difficulty_level, content, options_json, correct_answer, ai_analysis, created_at, updated_at) 
                VALUES (:bank_id, :question_type, :difficulty_level, :content, :options_json, :correct_answer, :ai_analysis, NOW(), NOW())
            ''')

            for q in questions:
                # 转为字典列表用于 JSON 序列化
                options_to_save = [opt.model_dump() for opt in q.options] if q.options else []

                db.execute(question_insert_sql, {
                    "bank_id": bank_id,
                    "question_type": q.question_type,
                    "difficulty_level": q.difficulty_level,
                    "content": q.content,
                    "options_json": json.dumps(options_to_save, ensure_ascii=False),
                    "correct_answer": json.dumps(q.correct_answer, ensure_ascii=False),
                    "ai_analysis": q.ai_analysis
                })
            
            db.commit()
            logger.info(f"==> 题库落库成功！Bank ID: {bank_id}。")

            return BankParseResponse(
                bank_id=bank_id,
                bank_name=bank_name,
                total_questions=len(questions),
                questions=questions
            )

        except Exception as e:
            db.rollback()
            logger.error(f"题库解析落库异常: {str(e)}")
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED, message="提取的题目入库失败")

ai_bank_service = AIBankService()