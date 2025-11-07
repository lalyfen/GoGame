"""
日志配置模块 - 用于配置日志轮转和归档
"""
import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging():
    """设置应用日志配置"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')

    # 确保日志目录存在
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    # 配置日志格式
    formatter = logging.Formatter(
        '[{asctime}] {levelname} [{name}] {pathname}:{lineno} - {message}',
        style='{'
    )

    access_formatter = logging.Formatter(
        '[{asctime}] ACCESS {levelname} [{name}] {message}',
        style='{'
    )

    # 设置日志轮转
    # Django主日志
    django_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOGS_DIR, 'django.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    django_handler.setFormatter(formatter)

    # 访问日志
    access_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOGS_DIR, 'access.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    access_handler.setFormatter(access_formatter)

    # 错误日志
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOGS_DIR, 'error.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # datab应用日志
    datab_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOGS_DIR, 'datab.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    datab_handler.setFormatter(formatter)

    # 设置日志记录器
    django_logger = logging.getLogger('django')
    django_logger.addHandler(django_handler)
    django_logger.addHandler(error_handler)

    access_logger = logging.getLogger('datab.access')
    access_logger.addHandler(access_handler)
    access_logger.addHandler(datab_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False

    datab_logger = logging.getLogger('datab')
    datab_logger.addHandler(datab_handler)
    datab_logger.addHandler(error_handler)
    datab_logger.setLevel(logging.DEBUG)
    datab_logger.propagate = False

    api_logger = logging.getLogger('api')
    api_logger.addHandler(datab_handler)
    api_logger.addHandler(error_handler)
    api_logger.setLevel(logging.INFO)
    api_logger.propagate = False

# 如果直接运行此脚本，设置日志
if __name__ == "__main__":
    setup_logging()