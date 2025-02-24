#!/bin/bash
# Ожидание готовности зависимостей (если нужно)
sleep 3
# Запуск Celery Beat
celery -A cargo beat --loglevel=info