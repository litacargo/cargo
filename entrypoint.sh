#!/bin/sh

# Выполняем миграции
python manage.py migrate

# Запускаем Gunicorn (Django)
gunicorn cargo.wsgi:application --bind 0.0.0.0:8000 &

# Запускаем Celery worker
celery -A cargo worker --loglevel=info &

# Запускаем Celery beat
celery -A cargo beat --loglevel=info &

# Ожидаем завершения всех процессов
wait