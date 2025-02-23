#!/bin/sh
echo "Current directory: $(/bin/pwd)"
echo "Listing files: $(ls -la)"

# Переходим в директорию с manage.py, если структура предполагает вложенность
cd /app/cargo || { echo "Failed to cd into /app/cargo"; exit 1; }

echo "New directory: $(/bin/pwd)"
echo "Listing files after cd: $(ls -la)"

echo "Running migrations..."
python manage.py migrate || { echo "Migrations failed with exit code $?"; exit 1; }
echo "Migrations completed successfully"

echo "Starting Gunicorn..."
exec gunicorn cargo.wsgi:application --bind 0.0.0.0:8000 --timeout 30 --log-level debug