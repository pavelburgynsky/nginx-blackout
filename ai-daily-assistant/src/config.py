"""Конфигурация приложения."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Настройки приложения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Telegram
    telegram_bot_token: str
    telegram_admin_ids: str = ""
    
    # AI Provider
    ai_provider: str = "anthropic"
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # Google Calendar
    google_calendar_credentials_file: str = "config/google_credentials.json"
    google_calendar_token_file: str = "config/google_token.json"
    
    # iTop
    itop_url: str = ""
    itop_api_key: str = ""
    itop_username: str = ""
    itop_password: str = ""
    
    # Database
    database_url: str = "sqlite:///./ai_assistant.db"
    
    # Application
    log_level: str = "INFO"
    timezone: str = "Europe/Moscow"
    
    # Task Planning
    work_start_time: str = "09:00"
    work_end_time: str = "18:00"
    default_task_duration: int = 30
    break_duration: int = 15
    lunch_duration: int = 60
    
    @property
    def admin_ids(self) -> List[int]:
        """Получить список ID администраторов."""
        if not self.telegram_admin_ids:
            return []
        return [int(id.strip()) for id in self.telegram_admin_ids.split(",") if id.strip()]
    
    def get_ai_api_key(self) -> str:
        """Получить API ключ для выбранного AI провайдера."""
        if self.ai_provider == "openai":
            return self.openai_api_key
        elif self.ai_provider == "anthropic":
            return self.anthropic_api_key
        else:
            raise ValueError(f"Неизвестный AI провайдер: {self.ai_provider}")
    
    def get_ai_model(self) -> str:
        """Получить модель для выбранного AI провайдера."""
        if self.ai_provider == "openai":
            return self.openai_model
        elif self.ai_provider == "anthropic":
            return self.anthropic_model
        else:
            raise ValueError(f"Неизвестный AI провайдер: {self.ai_provider}")


# Создаём глобальный экземпляр настроек
settings = Settings()
