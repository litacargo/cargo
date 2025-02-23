from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Product, Status
from config.models import Configuration
from config.config import BaseStatus
from notifications.notification_transit import notification_for_products_status_transit

@shared_task
def update_product_statuses():
    transit_hours = Configuration.objects.get(key="transit_hours")
    hours_value = int(transit_hours.value)
    hours_ago = timezone.now() - timedelta(hours=hours_value) # Получаем дату, которая находится на transit_hours часов назад
    status_china = Status.objects.get(name=BaseStatus.CHINA)
    products_in_china = Product.objects.filter(status=status_china, date__lte=hours_ago) # Получаем товары в Китае, которые находятся там более 2 дней

    updated_count = 0 # Количество обновленных товаров
    updated_ids = [] # Список обновленных товаров

    for product in products_in_china:
        product.status = Status.objects.get(name='В пути') # Обновляем статус
        product.date = timezone.now()  # Обновляем дату на текущую
        product.save() # Сохраняем изменения
        updated_count += 1  # Увеличиваем счетчик
        updated_ids.append(product.id) # Добавляем ID товара в список

    
    notification_for_products_status_transit.delay()
    return {
        'updated_count': updated_count,
        'updated_ids': updated_ids,
        'timestamp': datetime.now().isoformat(),
    }