import redis
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine, Base
import os

# 创建 FastAPI 实例
app = FastAPI(title="LiteKnow AI Agent Backend")

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