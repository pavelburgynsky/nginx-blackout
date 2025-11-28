"""Настройка логирования."""

import sys
from loguru import logger
from ..config import settings


def setup_logger():
    """Настроить логирование."""
    logger.remove()
    
    # Консольный вывод
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Файловый вывод
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=settings.log_level,
        rotation="00:00",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Логирование настроено")
