# Берем официальный образ Python
FROM python:3.11-slim

# Устанавливаем FFmpeg (это и есть решение проблемы)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем приложение (используем gunicorn)
CMD gunicorn --bind 0.0.0.0:$PORT app:app
