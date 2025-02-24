#!/bin/bash
# Ожидание готовности зависимостей (если нужно)
sleep 3
# Запуск Celery Worker
celery -A cargo worker --loglevel=info