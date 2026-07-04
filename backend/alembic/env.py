from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv
load_dotenv()
import sys
import os

# 将项目根目录加入 sys.path，确保 env.py 能正确导入 app 和 config 包
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.database import Base
# 导入 models 目录下的 .py 等模型文件
from models.attachments import Attachment
from models.bank_questions import BankQuestion
from models.favorites import Favorite
from models.messages import Message
from models.practice_records import PracticeRecord
from models.practice_sessions import PracticeSession
from models.question_banks import QuestionBank
from models.sessions import Session
from models.users import User
from models.wrong_questions import WrongQuestion
from models.database import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT")
dbname = os.getenv("MYSQL_DATABASE")
db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
