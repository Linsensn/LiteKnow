# backend/services/ai_quiz_service.py
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from utils.exceptions import CustomAPIException, ErrorCode 
from models.question_banks import QuestionBank
from models.bank_questions import BankQuestion
from services.message_service import msg_service
from schemas.message_schema import MessageCreate

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from schemas.ai_quiz_schema import QuizOutputData
from utils.llm_client import llm_client

logger = logging.getLogger("liteknow.ai_quiz")

class AIQuizService:
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
        
        user_msg_in = MessageCreate(
            session_id=session_id, role="user", content_type="text", content=user_content
        )
        await msg_service.create_message(db, obj_in=user_msg_in)

        parser = PydanticOutputParser(pydantic_object=QuizOutputData)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个严谨且专业的出题专家。请仔细阅读用户提供的课文要点，自主生成 {count} 道题目。\n"
                       "题目整体难度应控制在：{difficulty}（easy=简单, medium=中等, hard=困难）。\n"
                       "允许生成的题型包括：{types_str}。请根据知识点合理分配题型。\n\n"
                       "【重要格式要求】:\n{format_instructions}"),
            ("user", "课文素材：\n{user_content}")
        ]).partial(format_instructions=parser.get_format_instructions())
        
        llm = llm_client.get_langchain_chat_model(model_name=model_name, temperature=0.3)
        
        # 组装 LCEL 链：Prompt -> LLM -> Parser
        chain = prompt | llm | parser

        try:
            # result 直接就是一个 QuizOutputData 类型的 Python 对象！
            quiz_result: QuizOutputData = await chain.ainvoke({
                "count": question_count,
                "difficulty": difficulty,
                "types_str": question_types,
                "user_content": user_content
            })
            questions = quiz_result.questions
        except OutputParserException as e:
            logger.error(f"LangChain 解析异常: {str(e)}")
            raise CustomAPIException(code=ErrorCode.AI_VALIDATION_FAILED, message="AI 生成的数据格式不符，请重试。")
        except Exception as e:
            logger.error(f"LangChain 调用异常: {str(e)}")
            raise CustomAPIException(code=ErrorCode.AI_VALIDATION_FAILED, message=f"大模型响应超时或失败: {str(e)}")

        if not questions:
            raise CustomAPIException(code=ErrorCode.AI_VALIDATION_FAILED, message="AI 未能生成有效的题目。")

        try:
            if target_bank_id:
                result = db.execute(
                    select(QuestionBank).where(QuestionBank.id == target_bank_id, QuestionBank.user_id == user_id)
                )
                existing_bank = result.scalars().first()
                if not existing_bank:
                    raise CustomAPIException(code=ErrorCode.NOT_FOUND, message="指定的题库不存在或无权限追加")
                
                existing_bank.total_questions += len(questions)
                bank_id = existing_bank.id
                db.add(existing_bank)
            else:
                new_bank = QuestionBank(
                    user_id=user_id, bank_name=bank_name,
                    description=f"AI生成的测试题（难度:{difficulty}）",
                    total_questions=len(questions)
                )
                db.add(new_bank)
                db.flush() 
                bank_id = new_bank.id

            bank_questions_to_insert = [
                BankQuestion(
                    bank_id=bank_id, 
                    chapter_name=q.chapter_name,
                    question_type=q.question_type,
                    difficulty_level=q.difficulty_level,
                    content=q.content,
                    options_json=[opt.model_dump() for opt in q.options_json],
                    correct_answer=q.correct_answer,
                    ai_analysis=q.ai_analysis
                ) for q in questions
            ]
            db.add_all(bank_questions_to_insert)
            
            ai_msg_in = MessageCreate(
                session_id=session_id, role="assistant", content_type="text",
                content=f"为您生成了 {len(questions)} 道题目，我已仔细校验了全部答案的合理性并生成了题库。"
            )
            await msg_service.create_message(db, obj_in=ai_msg_in)
            
            db.commit()

            return {
                "bank_id": bank_id,
                "added_questions": len(questions),
                "is_append": target_bank_id is not None
            }

        except CustomAPIException as ce:
            db.rollback()
            raise ce
        except Exception as e:
            db.rollback()
            logger.error(f"测验生成与落库失败: {str(e)}")
            raise CustomAPIException(code=ErrorCode.DB_OPERATION_FAILED, message="智能测验处理入库失败")

ai_quiz_service = AIQuizService()