
import os
import sys
from loguru import logger
from config.settings import settings

def setup_logger():
    """
    初始化并配置项目全局日志系统。

    核心业务逻辑：
    1. 确保存储路径存在：检测容器内 /app/logs 路径，若缺失则自动创建，规避 Docker 挂载权限风险。
    2. 注册日志句柄：配置 loguru 处理器，注入日期占位符实现多文件管理。
    3. 性能优化：启用消息队列异步写入，防止 I/O 操作抢占 CPU 资源影响视觉算法识别速度。

    Args:
        无参数。

    Returns:
        loguru.logger: 返回经过预设配置的日志单例对象，支持在各业务模块中直接调用。

    Raises:
        OSError: 当宿主机挂载目录权限受限，导致无法在指定路径创建文件夹时抛出。
    """
    log_dir = "/app/logs"
    
    # 自动创建目录（防止 Docker 挂载时出现权限或路径问题）
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filepath = f"{log_dir}/liteknow_{{time:YYYY-MM-DD}}.log"
    # 动态判定日志级别
    log_level = "DEBUG" if settings.DEBUG else "INFO"

    # 移除 Loguru 默认自带的 handler（防止与后面的配置冲突或重复打印）
    logger.remove()

    # 显式添加控制台输出通道 (输出给 Docker logs 看的)
    logger.add(
        sys.stdout, 
        level=log_level,
        # 可以自定义控制台的颜色和格式，看起来更直观
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
        colorize=True
    )

    # 添加文件输出通道
    logger.add(
        log_filepath,
        rotation="00:00",
        retention="7 days",
        level=log_level,
        encoding="utf-8",
        enqueue=True
    )

    return logger