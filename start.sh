#!/bin/bash

# Переменные для путей (при необходимости подставьте свои)
PYTHON="python"  # или python3, если требуется
MANAGE_PY="./manage.py"
GUNICORN="gunicorn"
CELERY="celery"

# Применяем миграции
echo "Применяем миграции..."
$PYTHON $MANAGE_PY migrate
if [ $? -ne 0 ]; then
    echo "Ошибка при выполнении миграций!"
    exit 1
fi

# Собираем статические файлы (без подтверждения)
echo "Собираем статические файлы..."
$PYTHON $MANAGE_PY collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "Ошибка при сборе статических файлов!"
    exit 1
fi

# Запускаем Gunicorn в фоновом режиме
echo "Запускаем Gunicorn..."
$GUNICORN cargo.wsgi:application --bind 0.0.0.0:8000 &
GUNICORN_PID=$!
sleep 2  # Даем время на запуск

# Запускаем Celery Worker в фоновом режиме
echo "Запускаем Celery Worker..."
$CELERY -A cargo worker --loglevel=info &
CELERY_WORKER_PID=$!
sleep 2

# Запускаем Celery Beat в фоновом режиме
echo "Запускаем Celery Beat..."
$CELERY -A cargo beat --loglevel=info &
CELERY_BEAT_PID=$!

# Сохраняем PID процессов для возможной остановки
echo "Все процессы запущены!"
echo "PID Gunicorn: $GUNICORN_PID"
echo "PID Celery Worker: $CELERY_WORKER_PID"
echo "PID Celery Beat: $CELERY_BEAT_PID"

# Ожидаем завершения (опционально)
wait