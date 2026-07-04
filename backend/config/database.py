
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# 引入配置单例
from config.settings import settings

# 创建 SQLAlchemy 引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG, # 调试模式下输出 SQL 语句，生产环境建议关闭
    pool_pre_ping=True,  # 悲观测试：每次从池中拿连接前先 PING 一下，防止 MySQL 断开报错
    pool_size=10,        # 连接池基础大小
    max_overflow=20      # 在高峰期允许最多超出的连接数
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建声明性基类
Base = declarative_base()