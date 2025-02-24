#!/bin/bash
python manage.py makemigrations
sleep 1
python manage.py migrate
sleep 3
gunicorn cargo.wsgi:application --bind 0.0.0.0:8000