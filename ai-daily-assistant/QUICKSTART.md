# ⚡ Быстрый старт - AI Daily Assistant

## 5 шагов до запуска

### 1️⃣ Установка зависимостей

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Создание .env файла

```bash
cp .env.example .env
```

### 3️⃣ Получение токена Telegram бота

1. Напишите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

### 4️⃣ Получение API ключа для AI

**Anthropic Claude (рекомендуется):**
- Регистрация: https://www.anthropic.com
- API ключ: https://console.anthropic.com/

**OpenAI GPT:**
- Регистрация: https://openai.com
- API ключ: https://platform.openai.com/api-keys

### 5️⃣ Заполнение .env

Минимальная конфигурация:

```env
# Telegram
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_ADMIN_IDS=ваш_telegram_id

# AI (выберите один)
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=ваш_ключ_anthropic

# или
# AI_PROVIDER=openai
# OPENAI_API_KEY=ваш_ключ_openai
```

### 🚀 Запуск

```bash
# Способ 1: Напрямую
python main.py

# Способ 2: Через скрипт (Linux/Mac)
./run.sh

# Способ 3: Docker
docker-compose up -d
```

## ✅ Проверка работы

1. Найдите бота в Telegram по username
2. Отправьте `/start`
3. Попробуйте команды:
   - `/help` - справка
   - `/plan` - план на день
   - `/tasks` - список задач

## 📱 Основные команды

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу |
| `/plan` | Составить план на день |
| `/tasks` | Показать задачи |
| `/addtask <название>` | Добавить задачу |
| `/optimize` | Оптимизировать расписание |
| `/help` | Помощь |

## 💬 Примеры использования

```
Вы: /plan
Бот: [составит оптимальный план на день]

Вы: /addtask Написать отчет
Бот: ✅ Задача добавлена: Написать отчет

Вы: Как лучше организовать работу?
Бот: [даст рекомендации с помощью AI]
```

## 🔧 Дополнительная настройка

### Google Calendar

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Calendar API
3. Создайте OAuth credentials
4. Скачайте JSON как `config/google_credentials.json`

### iTop

Добавьте в `.env`:

```env
ITOP_URL=https://your-itop.com
ITOP_USERNAME=username
ITOP_PASSWORD=password
```

## ❓ Проблемы?

- 📖 Полная документация: [README.md](README.md)
- 🔧 Инструкция по установке: [INSTALL.md](INSTALL.md)
- 💡 Логи приложения: `logs/app_*.log`

## 🎉 Готово!

Ваш AI-ассистент готов помогать вам планировать день и управлять задачами!

---

**Нужна помощь?** Создайте issue на GitHub или проверьте документацию.
