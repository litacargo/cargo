from django.contrib.auth.models import User
from simple_history import register

# Регистрируем стандартную модель User для отслеживания истории
register(User)