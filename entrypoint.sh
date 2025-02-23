#!/bin/sh
# Выполняем миграции
python manage.py migrate

# Запускаем Celery в фоне
celery -A cargo worker --loglevel=info &
celery -A cargo beat --loglevel=info &

# Запускаем Gunicorn на переднем плане
exec gunicorn cargo.wsgi:application --bind 0.0.0.0:8000