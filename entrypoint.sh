#!/bin/sh
echo "Starting entrypoint script..."
echo "Current directory: $(/bin/pwd)"
echo "Listing files: $(ls -la)"
echo "Starting Gunicorn directly..."
exec gunicorn cargo.wsgi:application --bind 0.0.0.0:8000 --timeout 30 --log-level debug