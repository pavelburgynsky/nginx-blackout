"""Обработчики команд и сообщений Telegram бота."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

from ..database import get_db, User, Task, Event, Conversation
from ..config import settings
from ..ai import AIAssistant
from ..integrations import GoogleCalendarIntegration, ITopIntegration
from ..planner import TaskScheduler, ScheduleOptimizer


# Глобальные объекты (будут инициализированы при запуске)
ai_assistant = None
calendar_integration = None
itop_integration = None
task_scheduler = None
schedule_optimizer = None


def init_services():
    """Инициализация сервисов."""
    global ai_assistant, calendar_integration, itop_integration, task_scheduler, schedule_optimizer
    
    ai_assistant = AIAssistant()
    calendar_integration = GoogleCalendarIntegration()
    itop_integration = ITopIntegration()
    task_scheduler = TaskScheduler()
    schedule_optimizer = ScheduleOptimizer()


def setup_handlers(application: Application):
    """
    Настройка обработчиков команд.
    
    Args:
        application: Приложение Telegram бота
    """
    # Инициализация сервисов
    init_services()
    
    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("plan", plan_command))
    application.add_handler(CommandHandler("tasks", tasks_command))
    application.add_handler(CommandHandler("calendar", calendar_command))
    application.add_handler(CommandHandler("itop", itop_command))
    application.add_handler(CommandHandler("addtask", add_task_command))
    application.add_handler(CommandHandler("optimize", optimize_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик callback кнопок
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("Обработчики успешно настроены")


def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
    """Получить или создать пользователя."""
    db: Session = next(get_db())
    
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Создан новый пользователь: {telegram_id}")
        
        return user
    finally:
        db.close()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user
    get_or_create_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_message = f"""👋 Привет, {user.first_name}!

Я - твой персональный AI-помощник для планирования дня и управления задачами.

🎯 Что я умею:
• Составлять план работ на день
• Интегрироваться с Google Calendar
• Работать с задачами из iTop
• Давать рекомендации по оптимизации расписания
• Помогать в решении различных задач

📝 Основные команды:
/plan - Составить план на день
/tasks - Показать задачи
/calendar - События из календаря
/itop - Тикеты из iTop
/addtask - Добавить задачу
/optimize - Оптимизировать расписание
/settings - Настройки
/help - Помощь

Просто напиши мне сообщение, и я постараюсь помочь! 💪"""
    
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    help_text = """📚 Справка по командам:

/start - Начать работу с ботом
/help - Показать эту справку

📅 Планирование:
/plan - Составить оптимальный план на день
/optimize - Оптимизировать текущее расписание

✅ Задачи:
/tasks - Показать все задачи
/addtask - Добавить новую задачу

📆 Календарь:
/calendar - Показать события из Google Calendar

🎫 iTop:
/itop - Показать тикеты из iTop

⚙️ Настройки:
/settings - Настройки профиля

💬 Свободное общение:
Просто напиши мне сообщение, и я помогу с любым вопросом или задачей!"""
    
    await update.message.reply_text(help_text)


async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /plan - составление плана на день."""
    await update.message.reply_text("⏳ Формирую план на день...")
    
    try:
        user = get_or_create_user(update.effective_user.id)
        db: Session = next(get_db())
        
        try:
            # Получаем задачи пользователя
            tasks = db.query(Task).filter(
                Task.user_id == user.id,
                Task.status.in_(['pending', 'in_progress'])
            ).all()
            
            tasks_data = [{
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'estimated_duration': task.estimated_duration or 30,
                'status': task.status
            } for task in tasks]
            
            # Получаем события из календаря
            events_data = []
            if user.google_calendar_enabled:
                calendar_events = calendar_integration.get_events()
                events_data = [{
                    'title': event.get('summary', 'Без названия'),
                    'start_time': datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date'))),
                    'end_time': datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date'))),
                } for event in calendar_events if 'start' in event and 'end' in event]
            
            # Получаем тикеты из iTop
            tickets_data = []
            if user.itop_enabled:
                tickets = itop_integration.get_my_tickets(limit=20)
                tickets_data = tickets
            
            # Планируем задачи
            scheduled_items = task_scheduler.schedule_tasks(tasks_data, events_data)
            
            # Форматируем расписание
            schedule_text = task_scheduler.format_schedule(scheduled_items)
            
            # Получаем рекомендации от AI
            user_settings = {
                'work_start_time': user.work_start_time,
                'work_end_time': user.work_end_time,
                'timezone': user.timezone
            }
            
            ai_plan = await ai_assistant.generate_daily_plan(
                events=events_data,
                tasks=tasks_data,
                tickets=tickets_data,
                user_settings=user_settings
            )
            
            response = f"{schedule_text}\n\n💡 Рекомендации AI:\n{ai_plan}"
            
            await update.message.reply_text(response)
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Ошибка при составлении плана: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при составлении плана. Попробуйте позже."
        )


async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /tasks - показать задачи."""
    user = get_or_create_user(update.effective_user.id)
    db: Session = next(get_db())
    
    try:
        tasks = db.query(Task).filter(Task.user_id == user.id).all()
        
        if not tasks:
            await update.message.reply_text(
                "📝 У вас пока нет задач.\n\n"
                "Используйте /addtask чтобы добавить новую задачу."
            )
            return
        
        # Группируем по статусу
        pending = [t for t in tasks if t.status == 'pending']
        in_progress = [t for t in tasks if t.status == 'in_progress']
        completed = [t for t in tasks if t.status == 'completed']
        
        response = "📋 Ваши задачи:\n\n"
        
        if in_progress:
            response += "🔄 В работе:\n"
            for task in in_progress:
                response += f"  • {task.title} [{task.priority}]\n"
            response += "\n"
        
        if pending:
            response += "⏳ Запланировано:\n"
            for task in pending:
                response += f"  • {task.title} [{task.priority}]\n"
            response += "\n"
        
        if completed:
            response += f"✅ Выполнено: {len(completed)}\n"
        
        await update.message.reply_text(response)
    
    finally:
        db.close()


async def calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /calendar - показать события календаря."""
    await update.message.reply_text("📅 Загружаю события из календаря...")
    
    try:
        events = calendar_integration.get_events()
        
        if not events:
            await update.message.reply_text(
                "📅 На сегодня нет запланированных событий."
            )
            return
        
        response = "📅 События на сегодня:\n\n"
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'Без названия')
            
            # Парсим время
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = start_dt.strftime('%H:%M')
            except:
                time_str = start
            
            response += f"  • {time_str} - {summary}\n"
        
        await update.message.reply_text(response)
    
    except Exception as e:
        logger.error(f"Ошибка при получении событий календаря: {e}")
        await update.message.reply_text(
            "❌ Ошибка при загрузке календаря. "
            "Убедитесь, что Google Calendar настроен."
        )


async def itop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /itop - показать тикеты из iTop."""
    await update.message.reply_text("🎫 Загружаю тикеты из iTop...")
    
    try:
        tickets = itop_integration.get_my_tickets(limit=10)
        
        if not tickets:
            await update.message.reply_text("🎫 У вас нет активных тикетов в iTop.")
            return
        
        response = "🎫 Ваши тикеты в iTop:\n\n"
        
        for ticket in tickets:
            ref = ticket.get('ref', '')
            title = ticket.get('title', '')
            priority = ticket.get('priority', '')
            status = ticket.get('status', '')
            
            response += f"  • {ref}: {title}\n"
            response += f"    Приоритет: {priority}, Статус: {status}\n\n"
        
        await update.message.reply_text(response)
    
    except Exception as e:
        logger.error(f"Ошибка при получении тикетов iTop: {e}")
        await update.message.reply_text(
            "❌ Ошибка при загрузке тикетов. "
            "Убедитесь, что iTop настроен в файле .env"
        )


async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /addtask - добавить задачу."""
    # Проверяем аргументы
    if not context.args:
        await update.message.reply_text(
            "📝 Использование: /addtask <название задачи>\n\n"
            "Пример: /addtask Подготовить отчет"
        )
        return
    
    task_title = " ".join(context.args)
    
    user = get_or_create_user(update.effective_user.id)
    db: Session = next(get_db())
    
    try:
        task = Task(
            user_id=user.id,
            title=task_title,
            priority='medium',
            status='pending'
        )
        db.add(task)
        db.commit()
        
        await update.message.reply_text(f"✅ Задача добавлена: {task_title}")
    
    finally:
        db.close()


async def optimize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /optimize - оптимизация расписания."""
    await update.message.reply_text("🔍 Анализирую расписание...")
    
    try:
        user = get_or_create_user(update.effective_user.id)
        db: Session = next(get_db())
        
        try:
            # Получаем текущее расписание
            tasks = db.query(Task).filter(
                Task.user_id == user.id,
                Task.status.in_(['pending', 'in_progress'])
            ).all()
            
            tasks_data = [{
                'title': task.title,
                'priority': task.priority,
                'estimated_duration': task.estimated_duration or 30,
            } for task in tasks]
            
            events_data = []
            if user.google_calendar_enabled:
                calendar_events = calendar_integration.get_events()
                events_data = [{
                    'title': event.get('summary', 'Без названия'),
                    'start_time': datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date'))),
                    'end_time': datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date'))),
                } for event in calendar_events if 'start' in event and 'end' in event]
            
            # Создаем расписание
            scheduled_items = task_scheduler.schedule_tasks(tasks_data, events_data)
            
            # Анализируем
            analysis = schedule_optimizer.analyze_schedule(scheduled_items)
            
            # Получаем рекомендации от AI
            user_settings = {
                'work_start_time': user.work_start_time,
                'work_end_time': user.work_end_time,
            }
            
            ai_recommendations = await ai_assistant.optimize_schedule(
                scheduled_items,
                user_settings
            )
            
            response = "📊 Анализ расписания:\n\n"
            response += f"📝 Задач: {analysis['tasks_count']}\n"
            response += f"📅 Событий: {analysis['events_count']}\n"
            response += f"☕ Перерывов: {analysis['breaks_count']}\n"
            response += f"⏱️ Рабочее время: {int(analysis['total_work_time'])} мин\n\n"
            
            response += "💡 Рекомендации:\n"
            for rec in analysis['recommendations']:
                response += f"  {rec}\n"
            
            response += f"\n🤖 AI рекомендует:\n{ai_recommendations}"
            
            await update.message.reply_text(response)
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Ошибка при оптимизации расписания: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при анализе расписания."
        )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /settings - настройки."""
    user = get_or_create_user(update.effective_user.id)
    
    settings_text = f"""⚙️ Ваши настройки:

👤 Профиль:
  • Имя: {user.first_name or 'Не указано'}
  • Username: @{user.username or 'Не указано'}

⏰ Рабочее время:
  • Начало: {user.work_start_time}
  • Конец: {user.work_end_time}
  • Часовой пояс: {user.timezone}

🔗 Интеграции:
  • Google Calendar: {'✅ Включен' if user.google_calendar_enabled else '❌ Выключен'}
  • iTop: {'✅ Включен' if user.itop_enabled else '❌ Выключен'}

Для изменения настроек обратитесь к администратору или измените файл .env"""
    
    await update.message.reply_text(settings_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений."""
    user = get_or_create_user(update.effective_user.id)
    message_text = update.message.text
    
    # Сохраняем сообщение в историю
    db: Session = next(get_db())
    
    try:
        # Сохраняем сообщение пользователя
        user_conversation = Conversation(
            user_id=user.id,
            role='user',
            content=message_text
        )
        db.add(user_conversation)
        db.commit()
        
        # Получаем историю разговора (последние 10 сообщений)
        recent_conversations = db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).order_by(Conversation.created_at.desc()).limit(10).all()
        
        conversation_history = [
            {'role': conv.role, 'content': conv.content}
            for conv in reversed(recent_conversations[:-1])  # Исключаем текущее сообщение
        ]
        
        # Отправляем в AI
        await update.message.reply_text("🤔 Думаю...")
        
        # Получаем контекст (задачи, события)
        tasks = db.query(Task).filter(
            Task.user_id == user.id,
            Task.status.in_(['pending', 'in_progress'])
        ).limit(5).all()
        
        context_data = {
            'tasks': [{
                'title': task.title,
                'priority': task.priority,
                'status': task.status
            } for task in tasks],
            'user_settings': {
                'work_start_time': user.work_start_time,
                'work_end_time': user.work_end_time,
            }
        }
        
        response = await ai_assistant.chat(
            message=message_text,
            conversation_history=conversation_history,
            context=context_data
        )
        
        # Сохраняем ответ AI
        assistant_conversation = Conversation(
            user_id=user.id,
            role='assistant',
            content=response
        )
        db.add(assistant_conversation)
        db.commit()
        
        await update.message.reply_text(response)
    
    finally:
        db.close()


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback кнопок."""
    query = update.callback_query
    await query.answer()
    
    # Здесь можно добавить обработку различных callback кнопок
    await query.edit_message_text(text=f"Выбрано: {query.data}")
