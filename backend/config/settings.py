
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

ENV_FILE_PATH = os.getenv("ENV_FILE", ".env")

class Settings(BaseSettings):
    """
    全局配置类，默认从 .env 文件读取环境变量，未找到则使用下方定义的默认值
    
    Attributes:
        ENVIRONMENT (str): 运行环境，默认为 "development"。
        DEBUG (bool): 调试模式开关，默认为 True。
        MYSQL_HOST (str): 数据库主机地址，默认为 "127.0.0.1"。
        MYSQL_PORT (int): 数据库端口号，默认为 3306。
        MYSQL_USER (str): 数据库用户名，默认为 "root"。
        MYSQL_PASSWORD (str): 数据库密码，默认为 ""。
        MYSQL_DATABASE (str): 数据库名称，默认为 "liteknow_dev"。
        REDIS_HOST (str): Redis 主机地址，默认为 "127.0.0.1"。
        REDIS_PORT (int): Redis 端口号，默认为 6379。
        REDIS_DB (int): Redis 数据库编号，默认为 0。
        LLM_ENABLED (bool): 是否启用大模型功能，默认为 True。
        LLM_API_KEY (str): 大模型 API 密钥，默认为 "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"。
        LLM_BASE_URL (str): 大模型 API 基础 URL，默认为 "https://api.siliconflow.cn/v1"。
        LLM_MODEL_NAME (str): 大模型名称，默认为 "Qwen/Qwen2.5-7B-Instruct"。
        DATABASE_URL (str): 通过计算字段动态生成的数据库连接 URL，符合 SQLAlchemy 的规范。
        JWT_SECRET_KEY (str): JWT 鉴权的密钥，默认为 "liteknow_super_secret_key_2026_fallback"。
        JWT_ALGORITHM (str): JWT 鉴权使用的算法，默认为 "HS256"。
        ACCESS_TOKEN_EXPIRE_MINUTES (int): JWT 访问令牌的过期时间，单位为分钟，默认为 1440（即 24 小时）。
    """
    
    # 运行环境控制
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 数据库连接参数
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "liteknow_dev"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    WX_APPID: str = ""  # 添加默认值
    WX_SECRET: str = ""  # 添加默认值
    
    LLM_ENABLED: bool = True
    # 密钥
    LLM_API_KEY: str = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    # 接口地址
    LLM_BASE_URL: str = "https://api.siliconflow.cn/v1"
    # 模型名称
    LLM_MODEL_NAME: str = "Qwen/Qwen2.5-7B-Instruct"

    # JWT 鉴权配置
    JWT_SECRET_KEY: str = "liteknow_super_secret_key_2026_fallback"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        动态拼接 SQLAlchemy 数据库连接字符串。
        避免在 .env 中维护长串 URL，降低拼写出错概率。
        
        Args:
            无输入参数，由 pydantic 在实例化时自动调用。
        
        Returns:
            str: 格式化后的数据库连接 URL，符合 SQLAlchemy 的规范。
        """

        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"

    # 将 env_file 的值指向动态获取的路径
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, 
        env_file_encoding="utf-8", 
        extra="ignore" 
    )

# 实例化并暴露给全局使用
settings = Settings()