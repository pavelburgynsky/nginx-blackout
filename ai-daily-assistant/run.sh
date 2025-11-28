#!/bin/bash
# Скрипт для запуска AI Daily Assistant

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}  AI Daily Assistant - Запуск    ${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не установлен${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python найден: $(python3 --version)${NC}"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

# Активация виртуального окружения
echo -e "${GREEN}🔄 Активация виртуального окружения...${NC}"
source venv/bin/activate

# Установка зависимостей
if [ ! -f "venv/installed" ]; then
    echo -e "${YELLOW}📥 Установка зависимостей...${NC}"
    pip install -r requirements.txt
    touch venv/installed
else
    echo -e "${GREEN}✅ Зависимости уже установлены${NC}"
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Файл .env не найден${NC}"
    echo -e "${YELLOW}📝 Создайте файл .env на основе .env.example${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Конфигурация найдена${NC}"

# Создание директорий
mkdir -p logs config

# Запуск бота
echo -e "${GREEN}🚀 Запуск бота...${NC}"
echo ""
python main.py
