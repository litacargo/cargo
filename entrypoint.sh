#!/bin/sh
# Выполняем миграции
python manage.py migrate

# Запускаем Gunicorn на переднем плане
exec gunicorn cargo.wsgi:application --bind 0.0.0.0:8000