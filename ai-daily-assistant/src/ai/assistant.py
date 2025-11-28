"""AI ассистент для работы с пользователем."""

from typing import List, Dict, Optional
from loguru import logger
from ..config import settings
from .prompts import SYSTEM_PROMPTS


class AIAssistant:
    """Класс AI ассистента."""
    
    def __init__(self):
        """Инициализация AI ассистента."""
        self.provider = settings.ai_provider
        self.model = settings.get_ai_model()
        self.api_key = settings.get_ai_api_key()
        
        # Инициализация клиента в зависимости от провайдера
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Неподдерживаемый AI провайдер: {self.provider}")
        
        logger.info(f"AI ассистент инициализирован: {self.provider} ({self.model})")
    
    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> str:
        """
        Отправить сообщение AI ассистенту.
        
        Args:
            message: Сообщение пользователя
            conversation_history: История разговора
            system_prompt: Системный промпт (по умолчанию - основной)
            context: Дополнительный контекст (события, задачи и т.д.)
        
        Returns:
            Ответ AI ассистента
        """
        try:
            # Подготовка системного промпта
            if system_prompt is None:
                system_prompt = SYSTEM_PROMPTS["main"]
            
            # Добавление контекста в системный промпт
            if context:
                context_text = self._format_context(context)
                system_prompt += f"\n\nТекущий контекст:\n{context_text}"
            
            # Подготовка истории разговора
            if conversation_history is None:
                conversation_history = []
            
            # Вызов соответствующего API
            if self.provider == "openai":
                return await self._chat_openai(message, conversation_history, system_prompt)
            elif self.provider == "anthropic":
                return await self._chat_anthropic(message, conversation_history, system_prompt)
        
        except Exception as e:
            logger.error(f"Ошибка при обращении к AI: {e}")
            return "Извините, произошла ошибка при обработке запроса. Попробуйте ещё раз."
    
    async def _chat_openai(
        self,
        message: str,
        conversation_history: List[Dict],
        system_prompt: str
    ) -> str:
        """Чат с OpenAI API."""
        try:
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Ошибка OpenAI API: {e}")
            raise
    
    async def _chat_anthropic(
        self,
        message: str,
        conversation_history: List[Dict],
        system_prompt: str
    ) -> str:
        """Чат с Anthropic API."""
        try:
            # Anthropic использует другой формат для истории
            # Системный промпт передается отдельно
            messages = conversation_history.copy()
            messages.append({"role": "user", "content": message})
            
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Ошибка Anthropic API: {e}")
            raise
    
    def _format_context(self, context: Dict) -> str:
        """
        Форматировать контекст для передачи в AI.
        
        Args:
            context: Словарь с контекстом
        
        Returns:
            Отформатированный текст контекста
        """
        parts = []
        
        # События календаря
        if "events" in context and context["events"]:
            parts.append("=== События в календаре ===")
            for event in context["events"]:
                start = event.get("start_time", "")
                end = event.get("end_time", "")
                title = event.get("title", "")
                parts.append(f"- {start} - {end}: {title}")
        
        # Задачи
        if "tasks" in context and context["tasks"]:
            parts.append("\n=== Задачи ===")
            for task in context["tasks"]:
                title = task.get("title", "")
                priority = task.get("priority", "medium")
                status = task.get("status", "pending")
                parts.append(f"- [{priority}] {title} (статус: {status})")
        
        # Тикеты iTop
        if "tickets" in context and context["tickets"]:
            parts.append("\n=== Тикеты iTop ===")
            for ticket in context["tickets"]:
                ref = ticket.get("ref", "")
                title = ticket.get("title", "")
                priority = ticket.get("priority", "")
                status = ticket.get("status", "")
                parts.append(f"- {ref}: {title} (приоритет: {priority}, статус: {status})")
        
        # Настройки пользователя
        if "user_settings" in context:
            settings = context["user_settings"]
            parts.append("\n=== Настройки пользователя ===")
            parts.append(f"- Рабочее время: {settings.get('work_start_time')} - {settings.get('work_end_time')}")
            parts.append(f"- Часовой пояс: {settings.get('timezone')}")
        
        return "\n".join(parts)
    
    async def generate_daily_plan(
        self,
        events: List[Dict],
        tasks: List[Dict],
        tickets: Optional[List[Dict]] = None,
        user_settings: Optional[Dict] = None
    ) -> str:
        """
        Сгенерировать план работы на день.
        
        Args:
            events: События из календаря
            tasks: Задачи пользователя
            tickets: Тикеты из iTop
            user_settings: Настройки пользователя
        
        Returns:
            План работы на день
        """
        context = {
            "events": events,
            "tasks": tasks,
        }
        
        if tickets:
            context["tickets"] = tickets
        
        if user_settings:
            context["user_settings"] = user_settings
        
        message = "Составь оптимальный план работы на сегодня, учитывая все мои задачи и события."
        
        return await self.chat(
            message=message,
            system_prompt=SYSTEM_PROMPTS["task_planning"],
            context=context
        )
    
    async def optimize_schedule(
        self,
        current_schedule: List[Dict],
        user_settings: Optional[Dict] = None
    ) -> str:
        """
        Оптимизировать расписание.
        
        Args:
            current_schedule: Текущее расписание
            user_settings: Настройки пользователя
        
        Returns:
            Рекомендации по оптимизации
        """
        context = {
            "schedule": current_schedule
        }
        
        if user_settings:
            context["user_settings"] = user_settings
        
        message = "Проанализируй моё расписание на сегодня и предложи оптимизации."
        
        return await self.chat(
            message=message,
            system_prompt=SYSTEM_PROMPTS["schedule_optimization"],
            context=context
        )
    
    async def help_with_task(
        self,
        task_description: str,
        task_type: Optional[str] = None
    ) -> str:
        """
        Помочь с решением задачи.
        
        Args:
            task_description: Описание задачи
            task_type: Тип задачи (optional)
        
        Returns:
            Помощь в решении задачи
        """
        context = {}
        if task_type:
            context["task_type"] = task_type
        
        return await self.chat(
            message=task_description,
            system_prompt=SYSTEM_PROMPTS["task_analysis"],
            context=context
        )
