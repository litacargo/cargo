import logging
import requests
from celery import shared_task
from django.utils import timezone

from products.models import Product, Status
from clients.models import Client
from .config import TRANSIT_API_URL

from .headers import HEADERS

logger = logging.getLogger(__name__)


@shared_task
def notification_for_products_status_transit():
    """
    Задача, которая собирает все товары в статусе 'В пути' и отправляет уведомления
    пользователям в Telegram. Вызывается по расписанию (например, cron) или вручную.
    """
    # Получаем текущую дату (без времени)
    today = timezone.now().date()
    
    # Ищем статус с именем "В пути" (проверьте, как у вас называются статусы в БД)
    try:
        transit_status = Status.objects.get(name="В пути")
    except Status.DoesNotExist:
        logger.error("Не найден статус с именем 'В пути'. Проверьте настройки в БД.")
        return

    # Фильтруем товары, у которых статус = "В пути" и дата = сегодня.
    # Если вам нужно брать товары не только за сегодня, но и до сегодняшнего дня, меняйте фильтр на date__lte=today
    transit_products = Product.objects.filter(status=transit_status, date=today)

    # Сгруппируем товары по коду пользователя (Client.code)
    product_count_by_user = {}
    for product in transit_products:
        # Предполагаем, что у вас в модели Product есть поле client (ForeignKey -> Client)
        if not product.client:
            continue

        user_code = product.client.code
        if not user_code:
            continue

        product_count_by_user[user_code] = product_count_by_user.get(user_code, 0) + 1

    # Формируем список данных для передачи в Telegram-бот
    notification_data = [
        {
            "user_code": user_code,
            "count": count
        }
        for user_code, count in product_count_by_user.items()
    ]

    # Запускаем асинхронную (отложенную) задачу на отправку уведомлений
    if notification_data:
        task = send_notification_telegram_transit.delay(notification_data)
        return task.id
    else:
        logger.info("Нет товаров со статусом 'В пути' на сегодня.")
        return None


@shared_task
def send_notification_telegram_transit(data_list):
    """
    Отправка уведомления по статусу 'В пути' в телеграм-бот.
    data_list — это список словарей вида:
        [
          {"user_code": <str>, "count": <int>},
          ...
        ]
    """
    notifications = []

    # Собираем реальные chat_id пользователей и кол-во товаров
    for item in data_list:
        user_code = item["user_code"]
        count = item["count"]

        try:
            client = Client.objects.get(code=user_code)
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

    # Если есть что отправлять — формируем запрос
    if notifications:
        try:
            response = requests.post(TRANSIT_API_URL, headers=HEADERS, json=notifications)

            if response.status_code == 200:
                return("Уведомления о статусе 'В пути' успешно отправлены.")
            else:
                return(f"Ошибка при отправке уведомлений (статус {response.status_code}): {response.text}")
        except Exception as e:
            return(f"Исключение при отправке уведомлений: {e}")
    else:
        return("Нет пользователей с telegram_chat_id для отправки уведомлений.")