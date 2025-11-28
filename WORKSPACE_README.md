# 📁 Workspace Overview

Это рабочее пространство содержит несколько проектов.

## 🗂️ Проекты в этом workspace

### 1. 🤖 AI Daily Assistant
**Директория:** `ai-daily-assistant/`  
**Описание:** Персональный AI-помощник для планирования дня и управления задачами через Telegram  
**Статус:** ✅ Полностью готов к использованию  
**Технологии:** Python, Telegram Bot API, OpenAI/Anthropic, Google Calendar, iTop

**Что умеет:**
- 📅 Составлять оптимальный план работы на день
- 🤖 Помогать в решении различных задач с помощью AI
- 🗓️ Интегрироваться с Google Calendar
- 🎫 Работать с тикетами iTop
- ⚡ Оптимизировать расписание

**Документация:**
- [README.md](ai-daily-assistant/README.md) - Полная документация
- [QUICKSTART.md](ai-daily-assistant/QUICKSTART.md) - Быстрый старт
- [GETTING_STARTED.md](ai-daily-assistant/GETTING_STARTED.md) - С чего начать
- [EXAMPLES.md](ai-daily-assistant/EXAMPLES.md) - Примеры использования

**Быстрый старт:**
```bash
cd ai-daily-assistant
cp .env.example .env
# Отредактируйте .env
./run.sh
```

---

### 2. 🌐 nginx-blackout
**Описание:** Руководство по автоматическому включению страницы блэкаута на nginx  
**Статус:** ✅ Готов к использованию  
**Файлы:**
- `blackout.html` - Русская версия страницы блэкаута
- `blackout_en.html` - Английская версия
- `blackout_pl.html` - Польская версия
- `blackout_tr.html` - Турецкая версия
- `README.md` - Инструкция по настройке

**Описание:** Простое решение для автоматического показа страницы "блэкаута" (временного отключения сайта) в определенное время с помощью nginx.

---

## 🚀 Рекомендации

### Для начала работы с AI Daily Assistant:

1. Перейдите в директорию:
   ```bash
   cd ai-daily-assistant
   ```

2. Прочитайте [GETTING_STARTED.md](ai-daily-assistant/GETTING_STARTED.md)

3. Следуйте инструкциям в [QUICKSTART.md](ai-daily-assistant/QUICKSTART.md)

### Структура workspace:

```
/workspace/
├── ai-daily-assistant/     ← Главный проект - AI помощник
│   ├── src/                 Исходный код
│   ├── tests/               Тесты
│   ├── main.py              Точка входа
│   └── *.md                 Документация
│
├── blackout*.html          ← Проект nginx-blackout
├── README.md               Документация nginx-blackout
└── WORKSPACE_README.md     ← Этот файл
```

## 📞 Нужна помощь?

- **AI Daily Assistant:** Смотрите документацию в папке `ai-daily-assistant/`
- **nginx-blackout:** Смотрите `README.md` в корне workspace

---

*Последнее обновление: 28 ноября 2025*
