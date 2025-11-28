"""Главный файл для запуска AI Daily Assistant."""

import asyncio
import sys
from loguru import logger

from src.config import settings
from src.utils.logger import setup_logger
from src.bot import TelegramBot


def main():
    """Главная функция."""
    # Настройка логирования
    setup_logger()
    
    logger.info("=" * 50)
    logger.info("AI Daily Assistant v0.1.0")
    logger.info("=" * 50)
    
    # Проверка обязательных настроек
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN не указан в .env файле")
        sys.exit(1)
    
    if not settings.get_ai_api_key():
        logger.error(f"API ключ для {settings.ai_provider} не указан в .env файле")
        sys.exit(1)
    
    # Создание и запуск бота
    try:
        bot = TelegramBot()
        bot.setup()
        
        logger.info("Бот успешно запущен и готов к работе!")
        logger.info(f"AI провайдер: {settings.ai_provider}")
        logger.info(f"Модель: {settings.get_ai_model()}")
        
        bot.run()
    
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        logger.info("AI Daily Assistant остановлен")


if __name__ == "__main__":
    main()
