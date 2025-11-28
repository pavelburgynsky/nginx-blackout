"""Интеграция с Google Calendar API."""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os.path
import pickle
from loguru import logger
from ..config import settings


class GoogleCalendarIntegration:
    """Класс для работы с Google Calendar API."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        """Инициализация интеграции с Google Calendar."""
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Аутентификация в Google Calendar API."""
        try:
            # Загрузка сохраненных учетных данных
            if os.path.exists(settings.google_calendar_token_file):
                with open(settings.google_calendar_token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Если учетные данные недействительны или отсутствуют
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(settings.google_calendar_credentials_file):
                        logger.warning("Файл google_credentials.json не найден")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.google_calendar_credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Сохранение учетных данных для следующего запуска
                with open(settings.google_calendar_token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Успешно подключились к Google Calendar API")
        
        except Exception as e:
            logger.error(f"Ошибка при аутентификации Google Calendar: {e}")
            self.service = None
    
    def get_events(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Получить события из календаря.
        
        Args:
            start_date: Начальная дата (по умолчанию - сегодня)
            end_date: Конечная дата (по умолчанию - конец сегодняшнего дня)
            max_results: Максимальное количество событий
        
        Returns:
            Список событий
        """
        if not self.service:
            logger.warning("Google Calendar API не инициализирован")
            return []
        
        try:
            if start_date is None:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if end_date is None:
                end_date = start_date.replace(hour=23, minute=59, second=59)
            
            # Получение событий
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Получено {len(events)} событий из Google Calendar")
            
            return events
        
        except Exception as e:
            logger.error(f"Ошибка при получении событий из Google Calendar: {e}")
            return []
    
    def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Создать событие в календаре.
        
        Args:
            title: Название события
            start_time: Время начала
            end_time: Время окончания
            description: Описание
            location: Местоположение
            attendees: Список email участников
        
        Returns:
            Созданное событие или None
        """
        if not self.service:
            logger.warning("Google Calendar API не инициализирован")
            return None
        
        try:
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': settings.timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': settings.timezone,
                },
            }
            
            if description:
                event['description'] = description
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            logger.info(f"Создано событие: {title}")
            return created_event
        
        except Exception as e:
            logger.error(f"Ошибка при создании события в Google Calendar: {e}")
            return None
    
    def update_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Обновить существующее событие.
        
        Args:
            event_id: ID события
            title: Новое название
            start_time: Новое время начала
            end_time: Новое время окончания
            description: Новое описание
        
        Returns:
            Обновленное событие или None
        """
        if not self.service:
            logger.warning("Google Calendar API не инициализирован")
            return None
        
        try:
            # Получаем текущее событие
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Обновляем поля
            if title:
                event['summary'] = title
            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': settings.timezone,
                }
            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': settings.timezone,
                }
            if description:
                event['description'] = description
            
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Обновлено событие: {event_id}")
            return updated_event
        
        except Exception as e:
            logger.error(f"Ошибка при обновлении события в Google Calendar: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """
        Удалить событие из календаря.
        
        Args:
            event_id: ID события
        
        Returns:
            True если успешно удалено
        """
        if not self.service:
            logger.warning("Google Calendar API не инициализирован")
            return False
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Удалено событие: {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при удалении события из Google Calendar: {e}")
            return False
