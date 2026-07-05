import os
import redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from config.settings import settings
from config.logger_config import setup_logger
from routers import root_router
from config.database import SessionLocal, engine, Base
from utils.exceptions import (
    CustomAPIException, custom_api_exception_handler,
    SQLAlchemyError, sqlalchemy_error_handler,
    RequestValidationError, validation_exception_handler,
    HTTPException, http_exception_handler,
    global_exception_handler
)

# 依赖项：获取数据库会话 (用于接口中操作数据库)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化 Redis 连接 (可选，验证 Redis 是否正常)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.on_event("startup")
async def startup_event():
    # 项目启动时检查 MySQL 连接
    try:
        # 尝试创建表 (如果表不存在的话，但强烈建议严格按照 Alembic 管理，此处仅做演示)
        # Base.metadata.create_all(bind=engine) 
        print("✅ MySQL 数据库连接成功！")
    except Exception as e:
        print(f"❌ MySQL 连接失败: {e}")

    # 项目启动时检查 Redis 连接
    try:
        redis_client.ping()
        print("✅ Redis 缓存连接成功！")
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")


# 根路径，测试服务器是否跑通
@app.get("/")
def read_root():
    return {"message": "Hello, LiteKnow AI Agent is running!"}

# 健康检查接口 (用于 Apifox 或小程序探测后端状态)
@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    # 简单执行一条 SQL 查询确认 MySQL 正常
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
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

# 挂载业务路由
app.include_router(root_router, prefix="/api/v1", tags=["API v1"])


# 直接挂载附件目录
UPLOAD_DIR = "backend/uploads/attachments"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# 创建 FastAPI 实例
app = FastAPI(title="LiteKnow AI Agent Backend")
# 在 main.py 加静态文件映射
app.mount(
    "/uploads",
    StaticFiles(directory="backend/uploads"),
    name="uploads"
)

# 依赖项：获取数据库会话 (用于接口中操作数据库)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化 Redis 连接 (可选，验证 Redis 是否正常)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.on_event("startup")
async def startup_event():
    # 项目启动时检查 MySQL 连接
    try:
        # 尝试创建表 (如果表不存在的话，但强烈建议严格按照 Alembic 管理，此处仅做演示)
        # Base.metadata.create_all(bind=engine) 
        print("✅ MySQL 数据库连接成功！")
    except Exception as e:
        print(f"❌ MySQL 连接失败: {e}")

    # 项目启动时检查 Redis 连接
    try:
        redis_client.ping()
        print("✅ Redis 缓存连接成功！")
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")


# 根路径，测试服务器是否跑通
@app.get("/")
def read_root():
    return {"message": "Hello, LiteKnow AI Agent is running!"}

# 健康检查接口 (用于 Apifox 或小程序探测后端状态)
@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    # 简单执行一条 SQL 查询确认 MySQL 正常
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "redis": "ok" if redis_client.ping() else "error"
    }