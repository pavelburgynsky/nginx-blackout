"""Тесты для оптимизатора расписания."""

import pytest
from datetime import datetime, timedelta
from src.planner.optimizer import ScheduleOptimizer


def test_optimizer_initialization():
    """Тест инициализации оптимизатора."""
    optimizer = ScheduleOptimizer()
    assert optimizer is not None


def test_analyze_empty_schedule():
    """Тест анализа пустого расписания."""
    optimizer = ScheduleOptimizer()
    
    result = optimizer.analyze_schedule([])
    
    assert result['total_items'] == 0
    assert result['tasks_count'] == 0
    assert result['events_count'] == 0


def test_analyze_schedule_with_tasks():
    """Тест анализа расписания с задачами."""
    optimizer = ScheduleOptimizer()
    
    now = datetime.now()
    scheduled_items = [
        {
            'type': 'task',
            'title': 'Задача 1',
            'start_time': now,
            'end_time': now + timedelta(minutes=60),
            'priority': 'high'
        },
        {
            'type': 'task',
            'title': 'Задача 2',
            'start_time': now + timedelta(minutes=60),
            'end_time': now + timedelta(minutes=120),
            'priority': 'medium'
        }
    ]
    
    result = optimizer.analyze_schedule(scheduled_items)
    
    assert result['total_items'] == 2
    assert result['tasks_count'] == 2
    assert result['total_work_time'] == 120


def test_recommendations_generation():
    """Тест генерации рекомендаций."""
    optimizer = ScheduleOptimizer()
    
    now = datetime.now()
    # Создаем перегруженное расписание
    scheduled_items = []
    for i in range(10):
        scheduled_items.append({
            'type': 'task',
            'title': f'Задача {i+1}',
            'start_time': now + timedelta(minutes=i*60),
            'end_time': now + timedelta(minutes=(i+1)*60),
            'priority': 'high'
        })
    
    result = optimizer.analyze_schedule(scheduled_items)
    
    assert len(result['recommendations']) > 0
    assert isinstance(result['recommendations'], list)
