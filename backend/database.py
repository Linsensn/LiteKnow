import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

# 读取环境变量，注意 MYSQL_HOST 在 docker-compose 中定义为 mysql
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "liteknow_dev")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root_password")

# 构建 MySQL 连接 URL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建数据库会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 ORM 基类 (供 Alembic 和 Models 使用)
Base = declarative_base()