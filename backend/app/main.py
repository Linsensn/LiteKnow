# main.py
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.logger_config import setup_logger

logger = setup_logger()
is_prod = settings.ENVIRONMENT == "production"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("[liteknow 引擎启动] 正在进行硬件感知与模型挂载...")
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
from routers import system, admin_router, student_router
app.include_router(system.router)
app.include_router(admin_router.admin_router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(student_router.student_router, prefix="/api/v1/student", tags=["Student"])
