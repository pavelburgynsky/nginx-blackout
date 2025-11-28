"""AI модуль для работы с LLM."""

from .assistant import AIAssistant
from .prompts import SYSTEM_PROMPTS

__all__ = ["AIAssistant", "SYSTEM_PROMPTS"]
