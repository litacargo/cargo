# Используем Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app/cargo

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Собираем статику
RUN python manage.py collectstatic --noinput

# Открываем порты
EXPOSE 8000

# Копируем скрипт для запуска всех сервисов
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Запускаем приложение через скрипт
CMD ["/entrypoint.sh"]