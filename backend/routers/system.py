# routers/system.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from config.database import get_db

# 创建针对系统层面的路由实例
router = APIRouter(tags=["系统与健康检查"])

@router.get("/")
def read_root():
    return {"message": "Hello, LiteKnow AI Agent is running!"}

@router.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # 使用 text() 包装原生 SQL 语句以兼容 SQLAlchemy 2.0+
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        # 注意：若后续接入 Redis，需在此处补充 redis_client 的探测逻辑
        "redis": "pending" 
    }