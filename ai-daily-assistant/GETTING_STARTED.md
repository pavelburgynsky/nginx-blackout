# 🎯 С чего начать?

Добро пожаловать в **AI Daily Assistant**! Этот файл поможет вам быстро начать работу.

## 📋 Что это?

**AI Daily Assistant** - персональный AI-помощник в Telegram для:
- 📅 Планирования рабочего дня
- ✅ Управления задачами
- 🗓️ Работы с календарем (Google Calendar)
- 🎫 Управления тикетами (iTop)
- 🤖 Помощи в решении различных задач с AI

## ⚡ Быстрый старт (5 минут)

### Шаг 1: Установите зависимости

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Шаг 2: Создайте .env файл

```bash
cp .env.example .env
```

### Шаг 3: Получите токены

1. **Telegram Bot Token:**
   - Напишите [@BotFather](https://t.me/botfather)
   - Команда: `/newbot`
   - Скопируйте токен

2. **Anthropic API Key:**
   - Зарегистрируйтесь на https://www.anthropic.com
   - Получите ключ в https://console.anthropic.com/

### Шаг 4: Заполните .env

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_ADMIN_IDS=ваш_telegram_id
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=ваш_ключ
```

### Шаг 5: Запустите!

```bash
python main.py
```

## 📚 Что читать дальше?

### Новичкам
1. 📖 [QUICKSTART.md](QUICKSTART.md) - Подробный быстрый старт
2. 📖 [EXAMPLES.md](EXAMPLES.md) - Примеры использования
3. 📖 [README.md](README.md) - Полная документация

### Для установки
- 🔧 [INSTALL.md](INSTALL.md) - Детальная инструкция по установке
- 🐳 Docker: `docker-compose up -d`

### Для разработчиков
- 📊 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Обзор проекта
- 📝 [CHANGELOG.md](CHANGELOG.md) - История изменений
- 🧪 `tests/` - Юнит-тесты

## 🎮 Первые команды

После запуска найдите бота в Telegram и попробуйте:

```
/start     - Начало работы
/help      - Справка
/plan      - План на день
/addtask Моя первая задача
```

## ❓ Возникли проблемы?

1. **Бот не отвечает?**
   - Проверьте токен в .env
   - Убедитесь что бот запущен

2. **AI не работает?**
   - Проверьте API ключ
   - Убедитесь что есть интернет

3. **Другие вопросы?**
   - Смотрите [INSTALL.md](INSTALL.md) раздел "Устранение проблем"
   - Проверьте логи в `logs/`

## 🎉 Готово!

Теперь у вас есть личный AI-помощник! Используйте его для:
- ✅ Планирования дня
- 📝 Управления задачами
- 💡 Получения советов
- 🚀 Повышения продуктивности

---

**Приятного использования!** 🎊

Если вам понравился проект - поставьте ⭐ на GitHub!
