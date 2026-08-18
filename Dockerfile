# 1. Берем за основу чистый и легкий Linux с уже установленным Python 3.12
# (Используем 3.12, так как он стабильнее в Докере для ИИ-библиотек)
FROM python:3.12-slim

# 2. Устанавливаем системные пакеты и Node.js (для Tailwind CSS)
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Указываем рабочую папку внутри контейнера
WORKDIR /app

# 4. Копируем файлы со списками зависимостей
COPY requirements.txt .
COPY ai_manager/package.json ai_manager/package-lock.json* ./ai_manager/

# 5. Устанавливаем библиотеки Python и Node.js
RUN pip install --no-cache-dir -r requirements.txt
RUN cd ai_manager && npm install

# 6. Копируем весь остальный код твоего проекта внутрь
COPY . .

# 7. Открываем порт 8000 для доступа извне
EXPOSE 8000