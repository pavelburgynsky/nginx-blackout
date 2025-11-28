"""Тесты для планировщика задач."""

import pytest
from datetime import datetime, timedelta
from src.planner.scheduler import TaskScheduler


def test_task_scheduler_initialization():
    """Тест инициализации планировщика."""
    scheduler = TaskScheduler()
    assert scheduler.work_start == "09:00"
    assert scheduler.work_end == "18:00"


def test_schedule_tasks_empty():
    """Тест планирования без задач."""
    scheduler = TaskScheduler()
    tasks = []
    events = []
    
    result = scheduler.schedule_tasks(tasks, events)
    
    assert isinstance(result, list)
    assert len(result) == 0


def test_schedule_single_task():
    """Тест планирования одной задачи."""
    scheduler = TaskScheduler()
    
    tasks = [{
        'title': 'Тестовая задача',
        'priority': 'high',
        'estimated_duration': 60
    }]
    events = []
    
    result = scheduler.schedule_tasks(tasks, events)
    
    assert len(result) >= 1
    task_items = [item for item in result if item['type'] == 'task']
    assert len(task_items) == 1
    assert task_items[0]['title'] == 'Тестовая задача'


def test_priority_sorting():
    """Тест сортировки задач по приоритету."""
    scheduler = TaskScheduler()
    
    tasks = [
        {'title': 'Низкий', 'priority': 'low', 'estimated_duration': 30},
        {'title': 'Срочный', 'priority': 'urgent', 'estimated_duration': 30},
        {'title': 'Средний', 'priority': 'medium', 'estimated_duration': 30},
    ]
    
    sorted_tasks = scheduler._sort_tasks_by_priority(tasks)
    
    assert sorted_tasks[0]['title'] == 'Срочный'
    assert sorted_tasks[-1]['title'] == 'Низкий'


def test_format_schedule():
    """Тест форматирования расписания."""
    scheduler = TaskScheduler()
    
    now = datetime.now()
    scheduled_items = [
        {
            'type': 'task',
            'title': 'Задача 1',
            'start_time': now,
            'end_time': now + timedelta(minutes=30),
            'priority': 'high'
        }
    ]
    
    result = scheduler.format_schedule(scheduled_items)
    
    assert isinstance(result, str)
    assert 'Задача 1' in result
    assert '📅' in result
