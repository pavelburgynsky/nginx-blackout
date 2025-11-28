"""Основной класс Telegram бота."""

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from loguru import logger
from ..config import settings
from ..database import init_db
from . import handlers


class TelegramBot:
    """Класс Telegram бота."""
    
    def __init__(self):
        """Инициализация бота."""
        self.token = settings.telegram_bot_token
        self.application = None
        
        # Инициализация базы данных
        init_db()
        
        logger.info("Telegram бот инициализирован")
    
    def setup(self):
        """Настройка бота и обработчиков."""
        # Создание приложения
        self.application = Application.builder().token(self.token).build()
        
        # Настройка обработчиков
        handlers.setup_handlers(self.application)
        
        logger.info("Обработчики команд настроены")
    
    def run(self):
        """Запуск бота."""
        if not self.application:
            self.setup()
        
        logger.info("Запуск Telegram бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def stop(self):
        """Остановка бота."""
        if self.application:
            await self.application.stop()
            logger.info("Telegram бот остановлен")
