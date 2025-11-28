# 📦 Инструкция по установке AI Daily Assistant

## Быстрый старт

### Вариант 1: Автоматическая установка (Linux/Mac)

```bash
chmod +x run.sh
./run.sh
```

Скрипт автоматически:
- Создаст виртуальное окружение
- Установит все зависимости
- Проверит конфигурацию
- Запустит бота

### Вариант 2: Docker

```bash
# Сборка образа
docker-compose build

# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Вариант 3: Ручная установка

#### Шаг 1: Подготовка

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd ai-daily-assistant

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

#### Шаг 2: Установка зависимостей

```bash
pip install -r requirements.txt
```

#### Шаг 3: Настройка

Скопируйте и отредактируйте файл конфигурации:

```bash
cp .env.example .env
nano .env  # или используйте любой другой редактор
```

#### Шаг 4: Создание Telegram бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "My AI Assistant")
4. Введите username бота (например: "my_ai_assistant_bot")
5. Скопируйте полученный токен
6. Вставьте токен в `.env` файл:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

#### Шаг 5: Получение вашего Telegram ID

1. Найдите бота [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправьте команду `/start`
3. Скопируйте ваш ID
4. Вставьте в `.env` файл:
   ```
   TELEGRAM_ADMIN_IDS=your_telegram_id
   ```

#### Шаг 6: Настройка AI провайдера

##### Для Anthropic Claude (рекомендуется):

1. Зарегистрируйтесь на [Anthropic](https://www.anthropic.com)
2. Получите API ключ в [консоли](https://console.anthropic.com/)
3. Добавьте в `.env`:
   ```
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your_api_key_here
   ```

##### Для OpenAI GPT:

1. Зарегистрируйтесь на [OpenAI](https://openai.com)
2. Получите API ключ на [странице API](https://platform.openai.com/api-keys)
3. Добавьте в `.env`:
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_api_key_here
   ```

#### Шаг 7: Настройка Google Calendar (опционально)

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Calendar API:
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "Google Calendar API"
   - Нажмите "Enable"
4. Создайте OAuth 2.0 credentials:
   - Перейдите в "APIs & Services" → "Credentials"
   - Нажмите "Create Credentials" → "OAuth client ID"
   - Выберите "Desktop app"
   - Скачайте JSON файл
5. Сохраните файл как `config/google_credentials.json`
6. Обновите `.env`:
   ```
   GOOGLE_CALENDAR_CREDENTIALS_FILE=config/google_credentials.json
   ```

#### Шаг 8: Настройка iTop (опционально)

Если вы используете iTop для управления задачами:

```env
ITOP_URL=https://your-itop-instance.com
ITOP_USERNAME=your_username
ITOP_PASSWORD=your_password
# или
ITOP_API_KEY=your_api_key
```

#### Шаг 9: Запуск

```bash
python main.py
```

## Проверка установки

После запуска:

1. Найдите вашего бота в Telegram по username
2. Отправьте команду `/start`
3. Бот должен ответить приветственным сообщением

## Устранение проблем

### Ошибка: "TELEGRAM_BOT_TOKEN не указан"

**Решение**: Убедитесь, что файл `.env` создан и содержит корректный токен бота.

### Ошибка: "API ключ для ... не указан"

**Решение**: Проверьте, что в `.env` указан ключ для выбранного AI провайдера.

### Бот не отвечает в Telegram

**Проверьте**:
1. Правильность токена бота
2. Интернет соединение
3. Логи приложения в папке `logs/`

### Google Calendar не работает

**Решение**:
1. Убедитесь, что API включен в Google Cloud Console
2. Проверьте путь к файлу `google_credentials.json`
3. При первом запросе к Calendar появится окно авторизации

### iTop не работает

**Проверьте**:
1. Корректность URL (должен быть доступен)
2. Правильность учетных данных
3. Наличие прав доступа к API

## База данных

### SQLite (по умолчанию)

База данных создается автоматически при первом запуске.
Файл: `ai_assistant.db`

### PostgreSQL

Для использования PostgreSQL:

1. Установите PostgreSQL
2. Создайте базу данных:
   ```sql
   CREATE DATABASE ai_assistant;
   ```
3. Обновите `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/ai_assistant
   ```

## Обновление

```bash
# Получите последние изменения
git pull

# Обновите зависимости
pip install -r requirements.txt --upgrade

# Перезапустите бота
python main.py
```

## Резервное копирование

### База данных

```bash
# SQLite
cp ai_assistant.db ai_assistant_backup.db

# PostgreSQL
pg_dump ai_assistant > backup.sql
```

### Конфигурация

```bash
# Создайте бэкап .env (БЕЗ коммита в Git!)
cp .env .env.backup
```

## Безопасность

⚠️ **Важно**:
- Никогда не коммитьте `.env` файл в Git
- Храните API ключи в безопасности
- Регулярно обновляйте зависимости
- Используйте сильные пароли для базы данных

## Производственное развертывание

### Использование systemd (Linux)

Создайте файл `/etc/systemd/system/ai-assistant.service`:

```ini
[Unit]
Description=AI Daily Assistant Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/ai-daily-assistant
Environment="PATH=/path/to/ai-daily-assistant/venv/bin"
ExecStart=/path/to/ai-daily-assistant/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-assistant
sudo systemctl start ai-assistant
sudo systemctl status ai-assistant
```

### Просмотр логов

```bash
# Логи приложения
tail -f logs/app_$(date +%Y-%m-%d).log

# Логи systemd
sudo journalctl -u ai-assistant -f
```

## Поддержка

Если возникли проблемы:

1. Проверьте логи в папке `logs/`
2. Изучите раздел "Устранение проблем"
3. Создайте issue на GitHub с описанием проблемы

---

**Готово! Ваш AI Daily Assistant настроен и готов к работе! 🎉**
