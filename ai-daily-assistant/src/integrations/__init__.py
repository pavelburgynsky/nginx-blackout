"""Интеграции с внешними сервисами."""

from .google_calendar import GoogleCalendarIntegration
from .itop import ITopIntegration

__all__ = ["GoogleCalendarIntegration", "ITopIntegration"]
