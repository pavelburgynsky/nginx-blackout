"""Оптимизатор расписания."""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from loguru import logger


class ScheduleOptimizer:
    """Класс для оптимизации расписания."""
    
    def analyze_schedule(self, scheduled_items: List[Dict]) -> Dict:
        """
        Проанализировать расписание и дать рекомендации.
        
        Args:
            scheduled_items: Список запланированных элементов
        
        Returns:
            Анализ расписания и рекомендации
        """
        analysis = {
            'total_items': len(scheduled_items),
            'tasks_count': 0,
            'events_count': 0,
            'breaks_count': 0,
            'total_work_time': 0,
            'total_break_time': 0,
            'busy_periods': [],
            'free_periods': [],
            'recommendations': []
        }
        
        tasks = []
        events = []
        breaks = []
        
        for item in scheduled_items:
            duration = (item['end_time'] - item['start_time']).total_seconds() / 60
            
            if item['type'] == 'task':
                tasks.append(item)
                analysis['tasks_count'] += 1
                analysis['total_work_time'] += duration
            elif item['type'] == 'event':
                events.append(item)
                analysis['events_count'] += 1
                analysis['total_work_time'] += duration
            elif item['type'] == 'break':
                breaks.append(item)
                analysis['breaks_count'] += 1
                analysis['total_break_time'] += duration
        
        # Анализ загруженности
        analysis['busy_periods'] = self._find_busy_periods(scheduled_items)
        
        # Генерация рекомендаций
        analysis['recommendations'] = self._generate_recommendations(
            scheduled_items, tasks, events, breaks, analysis
        )
        
        return analysis
    
    def _find_busy_periods(self, scheduled_items: List[Dict]) -> List[Dict]:
        """
        Найти периоды высокой загруженности.
        
        Args:
            scheduled_items: Список запланированных элементов
        
        Returns:
            Список загруженных периодов
        """
        busy_periods = []
        
        if not scheduled_items:
            return busy_periods
        
        current_period_start = None
        current_period_end = None
        items_in_period = 0
        
        for i, item in enumerate(scheduled_items):
            if item['type'] == 'break':
                # Перерыв - завершаем текущий период
                if current_period_start and items_in_period >= 3:
                    busy_periods.append({
                        'start': current_period_start,
                        'end': current_period_end,
                        'items_count': items_in_period
                    })
                current_period_start = None
                items_in_period = 0
            else:
                if current_period_start is None:
                    current_period_start = item['start_time']
                current_period_end = item['end_time']
                items_in_period += 1
        
        # Проверяем последний период
        if current_period_start and items_in_period >= 3:
            busy_periods.append({
                'start': current_period_start,
                'end': current_period_end,
                'items_count': items_in_period
            })
        
        return busy_periods
    
    def _generate_recommendations(
        self,
        scheduled_items: List[Dict],
        tasks: List[Dict],
        events: List[Dict],
        breaks: List[Dict],
        analysis: Dict
    ) -> List[str]:
        """
        Сгенерировать рекомендации по оптимизации расписания.
        
        Args:
            scheduled_items: Все элементы расписания
            tasks: Задачи
            events: События
            breaks: Перерывы
            analysis: Результаты анализа
        
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Проверка общей загруженности
        if analysis['total_work_time'] > 480:  # Более 8 часов
            recommendations.append(
                "⚠️ Рабочий день перегружен (более 8 часов). "
                "Рекомендую перенести некоторые задачи на другой день."
            )
        
        # Проверка перерывов
        if analysis['breaks_count'] == 0 and analysis['total_work_time'] > 180:
            recommendations.append(
                "☕ Добавьте перерывы в расписание. "
                "Рекомендуется делать короткий перерыв каждые 1.5-2 часа."
            )
        
        # Проверка загруженных периодов
        if analysis['busy_periods']:
            for period in analysis['busy_periods']:
                duration = (period['end'] - period['start']).total_seconds() / 60
                if duration > 180:  # Более 3 часов без перерыва
                    recommendations.append(
                        f"⏰ Период {period['start'].strftime('%H:%M')} - "
                        f"{period['end'].strftime('%H:%M')} очень загружен ({period['items_count']} элементов). "
                        f"Рекомендую добавить перерыв."
                    )
        
        # Проверка приоритетов задач
        high_priority_tasks = [t for t in tasks if t.get('priority') in ['urgent', 'high']]
        if high_priority_tasks:
            first_high_priority = high_priority_tasks[0]
            if first_high_priority['start_time'].hour > 11:
                recommendations.append(
                    "💡 Рекомендую перенести важные задачи на утро, "
                    "когда продуктивность выше."
                )
        
        # Проверка буферного времени между встречами
        for i in range(len(events) - 1):
            current_end = events[i]['end_time']
            next_start = events[i + 1]['start_time']
            gap = (next_start - current_end).total_seconds() / 60
            
            if gap < 10 and gap > 0:
                recommendations.append(
                    f"⏱️ Мало времени между встречами "
                    f"({current_end.strftime('%H:%M')} - {next_start.strftime('%H:%M')}). "
                    f"Рекомендую добавить буфер 10-15 минут."
                )
        
        # Если рекомендаций нет
        if not recommendations:
            recommendations.append("✅ Расписание выглядит сбалансированно!")
        
        return recommendations
    
    def suggest_task_reordering(self, tasks: List[Dict]) -> List[Dict]:
        """
        Предложить переупорядочивание задач.
        
        Args:
            tasks: Список задач
        
        Returns:
            Оптимизированный порядок задач
        """
        # Сортируем по приоритету и типу задачи
        # Сложные задачи - утром, простые - днем
        
        priority_scores = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
        
        # Простая эвристика: задачи с высоким приоритетом и большой длительностью - в начало
        scored_tasks = []
        for task in tasks:
            priority = task.get('priority', 'medium')
            duration = task.get('estimated_duration', 30)
            
            score = priority_scores.get(priority, 2) * 10 + (duration / 60)
            scored_tasks.append((score, task))
        
        # Сортируем по убыванию score
        scored_tasks.sort(key=lambda x: x[0], reverse=True)
        
        return [task for _, task in scored_tasks]
