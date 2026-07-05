# backend/database.py
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True # 声明为抽象基类，不会在数据库中创建实体表
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    # 结合 SQL 规范，设定时间默认值与自动更新逻辑
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
   