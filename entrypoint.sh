#!/bin/sh
# Выполняем миграции
python manage.py migrate

# Запускаем Gunicorn на переднем плане
exec python manage.py runserver