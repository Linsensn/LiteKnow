# main.py
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.database import SessionLocal
from fastapi.openapi.utils import get_openapi

from config.settings import settings
from config.logger_config import setup_logger

logger = setup_logger()
is_prod = settings.ENVIRONMENT == "production"

from models.attachments import Attachment
from models.bank_questions import BankQuestion
from models.favorites import Favorite
from models.messages import Message
from models.practice_records import PracticeRecord
from models.practice_sessions import PracticeSession
from models.question_banks import QuestionBank
from models.sessions import Session as SessionModel
from models.users import User
from models.wrong_questions import WrongQuestion
from models.database import Base

from .db_seed_data import ( 
    SEED_USERS, SEED_QUESTION_BANKS, SEED_BANK_QUESTIONS, 
    SEED_PRACTICE_SESSIONS, SEED_PRACTICE_RECORDS, SEED_FAVORITES, 
    SEED_WRONG_QUESTIONS, SEED_SESSIONS, SEED_MESSAGES, SEED_ATTACHMENTS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("[liteknow 引擎启动] 正在进行硬件感知与模型挂载...")
    
    db = SessionLocal()
    try:
        init_db_data(db)
    finally:
        db.close() # 用完即刻释放连接
    
    logger.info("=" * 60)
    logger.info(f"交互式 API 文档 (Swagger) :  http://127.0.0.1:8000/docs")
    logger.info(f"备用 API 文档 (ReDoc)     :  http://127.0.0.1:8000/redoc")
    logger.info(f"系统当前运行环境          :  {settings.ENVIRONMENT.upper()}") 
    logger.info(f"前端 WebAR 调试地址       :  http://127.0.0.1/") 
    logger.info(f"日志平台                  :  http://127.0.0.1:8888/") 
    logger.info("=" * 60)

    yield 
    
    logger.info(">> 资源释放完毕，服务安全停止。")

app = FastAPI(
    title="LiteKnow AI Agent Backend", 
    lifespan=lifespan, 
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from utils.exceptions import (
    CustomAPIException, custom_api_exception_handler,
    SQLAlchemyError, sqlalchemy_error_handler,
    RequestValidationError, validation_exception_handler,
    HTTPException, http_exception_handler,
    global_exception_handler
)

app.add_exception_handler(CustomAPIException, custom_api_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 将路由挂载到 FastAPI 实例上
from routers import root_router
app.include_router(root_router, prefix="/api/v1")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # 1. 生成标准的 OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    
    # 2. 遍历所有路由，强制删除端点级别的 security 配置
    if "paths" in openapi_schema:
        for path_url, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                if isinstance(operation, dict) and "security" in operation:
                    del operation["security"]  # 核心：删除独立鉴权标签

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

def init_db_data(db: Session):
    """初始化数据库种子数据"""
    try:
        # 只需要检查有没有第一个基础用户，就能判断是不是空库
        first_user = db.query(User).filter(User.wechat_openid == "wx_o001").first()
        if not first_user:
            logger.info(">>> 检测到数据库为空，开始植入基础种子数据...")
            
            # 1. 插入用户数据 (无外键依赖)
            for u_data in SEED_USERS:
                db.add(User(**u_data))
            db.commit() 
            logger.info("  -  用户数据 (users) 初始化完成")

            # 2. 插入题库数据 (依赖 users)
            for bank_data in SEED_QUESTION_BANKS:
                db.add(QuestionBank(**bank_data))
            db.commit()
            logger.info("  -  题库数据 (question_banks) 初始化完成")

            # 3. 插入题目数据 (依赖 question_banks)
            for q_data in SEED_BANK_QUESTIONS:
                db.add(BankQuestion(**q_data))
            db.commit()
            logger.info("  -  题目数据 (bank_questions) 初始化完成")

            # 4. 插入会话数据 (依赖 users)
            for session_data in SEED_SESSIONS:
                db.add(SessionModel(**session_data))
            db.commit()
            logger.info("  -  会话数据 (sessions) 初始化完成")

            # 5. 插入消息数据 (依赖 sessions)
            for msg_data in SEED_MESSAGES:
                db.add(Message(**msg_data))
            db.commit()
            logger.info("  -  消息数据 (messages) 初始化完成")

            # 6. 插入附件数据 (依赖 users, messages)
            for att_data in SEED_ATTACHMENTS:
                db.add(Attachment(**att_data))
            db.commit()
            logger.info("  -  附件数据 (attachments) 初始化完成")

            # 7. 插入错题本数据 (依赖 users)
            for wq_data in SEED_WRONG_QUESTIONS:
                db.add(WrongQuestion(**wq_data))
            db.commit()
            logger.info("  -  错题本数据 (wrong_questions) 初始化完成")

            # 8. 插入收藏夹数据 (依赖 users, sessions)
            for fav_data in SEED_FAVORITES:
                db.add(Favorite(**fav_data))
            db.commit()
            logger.info("  -  收藏夹数据 (favorites) 初始化完成")

            # 9. 插入练习会话数据 (依赖 users, question_banks)
            for ps_data in SEED_PRACTICE_SESSIONS:
                db.add(PracticeSession(**ps_data))
            db.commit()
            logger.info("  -  练习会话数据 (practice_sessions) 初始化完成")

            # 10. 插入练习记录数据 (依赖 practice_sessions, users, bank_questions)
            for pr_data in SEED_PRACTICE_RECORDS:
                db.add(PracticeRecord(**pr_data))
            db.commit()
            logger.info("  -  练习记录数据 (practice_records) 初始化完成")

            logger.info(">>>  所有种子数据植入完毕！")
            
    except Exception as e:
        logger.error(f"种子数据初始化失败: {e}")
        db.rollback() # 发生错误时回滚，保护数据库干净

