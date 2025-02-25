import os
import openpyxl
from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Product, Status, Client
from config.models import Configuration
from config.config import BaseStatus

from notifications.notification_transit import notification_for_products_status_transit

from notifications.notification_china import send_notification_china
from notifications.notification_bishkek import send_notification_bihskek

from openpyxl import load_workbook

import logging
logger = logging.getLogger(__name__)


# @shared_task
# def process_china_products(file_path, request_user_id):
#     try:
#         # ... логика ...
#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)



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



@shared_task
def process_china_products(file_path, request_user_id):
    """
    Асинхронная обработка файла с товарами для Китая.
    file_path: путь к временно сохраненному файлу
    request_user_id: ID пользователя для отправки сообщений (если нужно)
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        products_created = 0
        products_skipped = 0
        clients_products_count = {}

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if len(row) < 1 or not row[0]:
                continue

            product_code = str(row[0]).strip()
            client_id = None
            client = None

            if len(row) >= 2 and row[1] is not None:
                client_id = row[1]
                if isinstance(client_id, float):
                    client_id = str(int(client_id))
                else:
                    client_id = str(client_id).strip()

                client = Client.objects.filter(code=client_id).first()
                if not client:
                    # Сообщения не работают напрямую в Celery, логируем или сохраняем отдельно
                    pass  # Можно добавить логирование

            china_status, _ = Status.objects.get_or_create(name=BaseStatus.CHINA)

            if client and Product.objects.filter(product_code=product_code, client=client).exists():
                products_skipped += 1
                continue
            elif not client and Product.objects.filter(product_code=product_code, client__isnull=True).exists():
                products_skipped += 1
                continue

            Product.objects.create(
                product_code=product_code,
                client=client,
                date=datetime.utcnow(),
                status=china_status,
                branch=client.branch if client else None
            )
            products_created += 1

            if client and client.id not in clients_products_count:
                clients_products_count[client.id] = 0
            if client:
                clients_products_count[client.id] += 1

        # Здесь можно отправить уведомление или сохранить результат
        if products_created > 0:
            # messages.success не работает в задаче, нужно использовать другой способ
            pass
        if products_skipped > 0:
            pass
        if clients_products_count:
            send_notification_china.delay(clients_products_count)

        return {
            "products_created": products_created,
            "products_skipped": products_skipped,
            "clients_products_count": clients_products_count
        }

    except Exception as e:
        # Логируем ошибку или сохраняем её для пользователя
        return {"error": str(e)}
    

@shared_task
def process_bishkek_products(file_path, request_user_id):
    """
    Асинхронная обработка файла с товарами для Бишкека.
    file_path: путь к временно сохраненному файлу
    request_user_id: ID пользователя для отправки сообщений (если нужно)
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        products_created = 0
        products_updated = 0
        clients_products_count = {}

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if len(row) < 2 or not row[0] or not row[2]:
                continue

            product_code = str(row[0]).strip()
            client_id = row[1] if len(row) > 1 else None
            weight = row[2]
            price = row[3] if len(row) > 3 else None

            client = None
            if client_id:
                if isinstance(client_id, float):
                    client_id = str(int(client_id))
                else:
                    client_id = str(client_id).strip()

                client = Client.objects.filter(code=client_id).first()
                if not client:
                    # Логируем предупреждение, так как messages не работает в Celery
                    pass

            bishkek_status, _ = Status.objects.get_or_create(name=BaseStatus.BISHKEK)

            product, created = Product.objects.get_or_create(
                product_code=product_code,
                client=client,
                defaults={
                    "status": bishkek_status,
                    "weight": weight,
                    "date": datetime.now().date(),
                }
            )

            if created:
                products_created += 1
            else:
                product.weight = weight
                product.status = bishkek_status
                if price is not None:
                    product.price = price
                product.save()
                products_updated += 1

            if client and client.id not in clients_products_count:
                clients_products_count[client.id] = 0
            if client:
                clients_products_count[client.id] += 1

        # Возвращаем результат для дальнейшего использования
        if clients_products_count:
            send_notification_bihskek.delay(clients_products_count)

        return {
            "products_created": products_created,
            "products_updated": products_updated,
            "clients_products_count": clients_products_count
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)  # Очищаем временный файл