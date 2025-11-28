"""Интеграция с iTop API."""

import requests
from typing import List, Dict, Optional
from loguru import logger
from ..config import settings


class ITopIntegration:
    """Класс для работы с iTop API."""
    
    def __init__(self):
        """Инициализация интеграции с iTop."""
        self.base_url = settings.itop_url.rstrip('/')
        self.api_url = f"{self.base_url}/webservices/rest.php"
        self.api_key = settings.itop_api_key
        self.username = settings.itop_username
        self.password = settings.itop_password
        
        if not self.base_url or not (self.api_key or (self.username and self.password)):
            logger.warning("iTop не настроен. Укажите URL и учетные данные в .env")
    
    def _make_request(self, operation: str, data: Dict) -> Optional[Dict]:
        """
        Выполнить запрос к iTop API.
        
        Args:
            operation: Тип операции (core/get, core/create и т.д.)
            data: Данные запроса
        
        Returns:
            Результат запроса или None
        """
        try:
            payload = {
                'version': '1.3',
                'operation': operation,
                'json_data': data
            }
            
            # Аутентификация
            if self.api_key:
                payload['auth_user'] = self.username
                payload['auth_pwd'] = self.api_key
            else:
                payload['auth_user'] = self.username
                payload['auth_pwd'] = self.password
            
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') != 0:
                logger.error(f"Ошибка iTop API: {result.get('message')}")
                return None
            
            return result
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к iTop API: {e}")
            return None
    
    def get_my_tickets(self, limit: int = 50) -> List[Dict]:
        """
        Получить список своих тикетов.
        
        Args:
            limit: Максимальное количество тикетов
        
        Returns:
            Список тикетов
        """
        try:
            # OQL запрос для получения тикетов текущего пользователя
            oql = f"SELECT UserRequest WHERE agent_id = '{self.username}' AND status != 'closed'"
            
            data = {
                'class': 'UserRequest',
                'key': oql,
                'output_fields': '*'
            }
            
            result = self._make_request('core/get', data)
            
            if not result:
                return []
            
            tickets = []
            objects = result.get('objects', {})
            
            for ticket_id, ticket_data in objects.items():
                fields = ticket_data.get('fields', {})
                tickets.append({
                    'id': ticket_id,
                    'ref': fields.get('ref', ''),
                    'title': fields.get('title', ''),
                    'description': fields.get('description', ''),
                    'status': fields.get('status', ''),
                    'priority': fields.get('priority', ''),
                    'start_date': fields.get('start_date', ''),
                    'caller_id': fields.get('caller_id', ''),
                })
            
            logger.info(f"Получено {len(tickets)} тикетов из iTop")
            return tickets[:limit]
        
        except Exception as e:
            logger.error(f"Ошибка при получении тикетов из iTop: {e}")
            return []
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        Получить информацию о конкретном тикете.
        
        Args:
            ticket_id: ID или ref тикета
        
        Returns:
            Информация о тикете или None
        """
        try:
            data = {
                'class': 'UserRequest',
                'key': ticket_id,
                'output_fields': '*'
            }
            
            result = self._make_request('core/get', data)
            
            if not result or not result.get('objects'):
                logger.warning(f"Тикет {ticket_id} не найден")
                return None
            
            ticket_data = list(result['objects'].values())[0]
            fields = ticket_data.get('fields', {})
            
            return {
                'id': list(result['objects'].keys())[0],
                'ref': fields.get('ref', ''),
                'title': fields.get('title', ''),
                'description': fields.get('description', ''),
                'status': fields.get('status', ''),
                'priority': fields.get('priority', ''),
                'start_date': fields.get('start_date', ''),
                'end_date': fields.get('end_date', ''),
                'caller_id': fields.get('caller_id', ''),
                'agent_id': fields.get('agent_id', ''),
            }
        
        except Exception as e:
            logger.error(f"Ошибка при получении тикета {ticket_id} из iTop: {e}")
            return None
    
    def update_ticket(
        self,
        ticket_id: str,
        status: Optional[str] = None,
        comment: Optional[str] = None
    ) -> bool:
        """
        Обновить тикет.
        
        Args:
            ticket_id: ID тикета
            status: Новый статус
            comment: Комментарий
        
        Returns:
            True если успешно обновлено
        """
        try:
            fields = {}
            
            if status:
                fields['status'] = status
            
            data = {
                'class': 'UserRequest',
                'key': ticket_id,
                'fields': fields
            }
            
            if comment:
                data['comment'] = comment
            
            result = self._make_request('core/update', data)
            
            if result:
                logger.info(f"Тикет {ticket_id} успешно обновлен")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Ошибка при обновлении тикета {ticket_id}: {e}")
            return False
    
    def get_tickets_stats(self) -> Dict:
        """
        Получить статистику по тикетам.
        
        Returns:
            Словарь со статистикой
        """
        try:
            tickets = self.get_my_tickets(limit=1000)
            
            stats = {
                'total': len(tickets),
                'by_status': {},
                'by_priority': {},
            }
            
            for ticket in tickets:
                # По статусу
                status = ticket.get('status', 'unknown')
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # По приоритету
                priority = ticket.get('priority', 'unknown')
                stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            return stats
        
        except Exception as e:
            logger.error(f"Ошибка при получении статистики тикетов: {e}")
            return {}
