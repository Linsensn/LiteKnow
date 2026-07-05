# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings 

# 创建 SQLAlchemy 引擎
engine = create_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG, 
    pool_pre_ping=True,  
    pool_size=10,        
    max_overflow=20      
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

# 创建声明性基类
Base = declarative_base() 

# 将依赖项移动到此处
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close() 