import logging
import json
import requests
import json
from celery import shared_task
from clients.models import Client
from .config import CHINA_API_URL
from .headers import HEADERS

logger = logging.getLogger(__name__)

@shared_task
def send_notification_china(data_dict: dict):
    notifications = []

    for user_code, count in data_dict.items():  # user_code = 101, count = 1
        try:
            client = Client.objects.get(id=user_code)
        except Client.DoesNotExist:
            logger.error(f"Клиент с user_code={user_code} не найден в базе.")
            continue

        if not client.telegram_chat_id:
            logger.warning(f"У клиента {user_code} отсутствует telegram_chat_id.")
            continue
        
        notifications.append({
            "telegram_chat_id": client.telegram_chat_id,
            "count": count
        })
    
    if notifications:
        try:
            response = requests.post(CHINA_API_URL, headers=HEADERS, json=notifications)
            if response.status_code == 200:
                return "Уведомления о статусе 'В пути' успешно отправлены."
            else:
                return f"Ошибка при отправке уведомлений (статус {response.status_code}): {response.text}"
        except Exception as e:
            return f"Исключение при отправке уведомлений: {e}"
    else:
        return "Нет пользователей с telegram_chat_id для отправки уведомлений."