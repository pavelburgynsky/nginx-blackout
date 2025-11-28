"""Планировщик задач."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger
from ..config import settings


class TaskScheduler:
    """Класс для планирования задач в течение дня."""
    
    def __init__(self, work_start: str = None, work_end: str = None):
        """
        Инициализация планировщика.
        
        Args:
            work_start: Время начала рабочего дня (HH:MM)
            work_end: Время окончания рабочего дня (HH:MM)
        """
        self.work_start = work_start or settings.work_start_time
        self.work_end = work_end or settings.work_end_time
        self.default_task_duration = settings.default_task_duration
        self.break_duration = settings.break_duration
        self.lunch_duration = settings.lunch_duration
    
    def schedule_tasks(
        self,
        tasks: List[Dict],
        events: List[Dict],
        date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Запланировать задачи с учетом существующих событий.
        
        Args:
            tasks: Список задач для планирования
            events: Существующие события в календаре
            date: Дата для планирования (по умолчанию - сегодня)
        
        Returns:
            Список запланированных задач и событий
        """
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Парсим рабочее время
        work_start_time = self._parse_time(self.work_start, date)
        work_end_time = self._parse_time(self.work_end, date)
        
        # Получаем свободные слоты
        free_slots = self._get_free_slots(work_start_time, work_end_time, events)
        
        # Сортируем задачи по приоритету
        sorted_tasks = self._sort_tasks_by_priority(tasks)
        
        # Планируем задачи в свободных слотах
        scheduled_items = []
        
        # Добавляем существующие события
        for event in events:
            scheduled_items.append({
                'type': 'event',
                'title': event.get('title', ''),
                'start_time': event.get('start_time'),
                'end_time': event.get('end_time'),
                'data': event
            })
        
        # Планируем задачи
        current_slot_index = 0
        tasks_since_break = 0
        
        for task in sorted_tasks:
            if current_slot_index >= len(free_slots):
                logger.warning(f"Не хватает времени для планирования задачи: {task.get('title')}")
                break
            
            # Определяем длительность задачи
            duration = task.get('estimated_duration', self.default_task_duration)
            
            # Пытаемся найти подходящий слот
            scheduled = False
            while current_slot_index < len(free_slots) and not scheduled:
                slot = free_slots[current_slot_index]
                slot_duration = (slot['end'] - slot['start']).total_seconds() / 60
                
                if slot_duration >= duration:
                    # Планируем задачу в этом слоте
                    task_start = slot['start']
                    task_end = task_start + timedelta(minutes=duration)
                    
                    scheduled_items.append({
                        'type': 'task',
                        'title': task.get('title', ''),
                        'start_time': task_start,
                        'end_time': task_end,
                        'priority': task.get('priority', 'medium'),
                        'data': task
                    })
                    
                    # Обновляем слот
                    free_slots[current_slot_index]['start'] = task_end
                    tasks_since_break += 1
                    scheduled = True
                    
                    # Добавляем перерыв, если нужно
                    if tasks_since_break >= 2:  # Перерыв каждые 2 задачи (примерно каждые 1.5 часа)
                        break_end = task_end + timedelta(minutes=self.break_duration)
                        if break_end <= slot['end']:
                            scheduled_items.append({
                                'type': 'break',
                                'title': 'Перерыв',
                                'start_time': task_end,
                                'end_time': break_end,
                            })
                            free_slots[current_slot_index]['start'] = break_end
                            tasks_since_break = 0
                else:
                    current_slot_index += 1
        
        # Сортируем по времени начала
        scheduled_items.sort(key=lambda x: x['start_time'])
        
        return scheduled_items
    
    def _get_free_slots(
        self,
        work_start: datetime,
        work_end: datetime,
        events: List[Dict]
    ) -> List[Dict]:
        """
        Получить свободные временные слоты.
        
        Args:
            work_start: Начало рабочего дня
            work_end: Конец рабочего дня
            events: События в календаре
        
        Returns:
            Список свободных слотов
        """
        # Сортируем события по времени начала
        sorted_events = sorted(events, key=lambda x: x.get('start_time', work_start))
        
        free_slots = []
        current_time = work_start
        
        # Добавляем обеденный перерыв
        lunch_start = work_start.replace(hour=13, minute=0)
        lunch_end = lunch_start + timedelta(minutes=self.lunch_duration)
        
        for event in sorted_events:
            event_start = event.get('start_time', current_time)
            event_end = event.get('end_time', event_start)
            
            # Если есть свободное время до события
            if current_time < event_start:
                # Проверяем, не пересекается ли с обедом
                if current_time < lunch_start < event_start:
                    # Добавляем слот до обеда
                    if current_time < lunch_start:
                        free_slots.append({'start': current_time, 'end': lunch_start})
                    # Обновляем текущее время после обеда
                    current_time = max(lunch_end, event_start)
                else:
                    free_slots.append({'start': current_time, 'end': event_start})
            
            # Обновляем текущее время
            current_time = max(current_time, event_end)
        
        # Добавляем оставшееся время после последнего события
        if current_time < work_end:
            # Проверяем обед
            if current_time < lunch_start < work_end:
                if current_time < lunch_start:
                    free_slots.append({'start': current_time, 'end': lunch_start})
                if lunch_end < work_end:
                    free_slots.append({'start': lunch_end, 'end': work_end})
            else:
                free_slots.append({'start': current_time, 'end': work_end})
        
        return free_slots
    
    def _sort_tasks_by_priority(self, tasks: List[Dict]) -> List[Dict]:
        """
        Сортировать задачи по приоритету.
        
        Args:
            tasks: Список задач
        
        Returns:
            Отсортированный список задач
        """
        priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        return sorted(
            tasks,
            key=lambda x: priority_order.get(x.get('priority', 'medium'), 2)
        )
    
    def _parse_time(self, time_str: str, date: datetime) -> datetime:
        """
        Парсить строку времени в datetime.
        
        Args:
            time_str: Строка времени (HH:MM)
            date: Дата
        
        Returns:
            Объект datetime
        """
        hour, minute = map(int, time_str.split(':'))
        return date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def format_schedule(self, scheduled_items: List[Dict]) -> str:
        """
        Форматировать расписание для отображения.
        
        Args:
            scheduled_items: Список запланированных элементов
        
        Returns:
            Отформатированная строка расписания
        """
        lines = ["📅 Ваше расписание на сегодня:\n"]
        
        for item in scheduled_items:
            start = item['start_time'].strftime('%H:%M')
            end = item['end_time'].strftime('%H:%M')
            title = item['title']
            item_type = item['type']
            
            if item_type == 'task':
                priority = item.get('priority', 'medium')
                emoji = self._get_priority_emoji(priority)
                lines.append(f"{emoji} {start} - {end}: {title}")
            elif item_type == 'event':
                lines.append(f"📌 {start} - {end}: {title}")
            elif item_type == 'break':
                lines.append(f"☕ {start} - {end}: {title}")
        
        return "\n".join(lines)
    
    def _get_priority_emoji(self, priority: str) -> str:
        """Получить emoji для приоритета."""
        emoji_map = {
            'urgent': '🔴',
            'high': '🟡',
            'medium': '🟢',
            'low': '⚪'
        }
        return emoji_map.get(priority, '🟢')
