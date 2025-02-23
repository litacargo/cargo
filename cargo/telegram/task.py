from celery import shared_task
import requests

@shared_task
def send_nottification_for_all_users(task_id: int, message: str, photo_urls=None):
    """
    task_id: ID записи NotificationTask в БД.
    message: текст сообщения (пригодится как 'massage' или 'caption' к фото).
    photo_urls: список URL-адресов (str) на изображения,
                например ["https://site.com/image1.jpg", "https://site.com/image2.jpg"].
                Если None или пустой список - значит, фото нет.
    """
    from .models import NotificationTask  # чтобы избежать циклических импортов
    from .config import TELEGRAM_API_KEY, TELEGRAM_API_URL

    if photo_urls is None:
        photo_urls = []

    task = NotificationTask.objects.get(id=task_id)
    task.status = 'pending'
    task.save()

    try:
        # Случай 1: Если нет фото, отправляем только текст
        if not photo_urls:
            url = f"{TELEGRAM_API_URL}/api/v1/send_message"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": TELEGRAM_API_KEY
            }
            payload = {
                "text": message,     # На вашем бэке это поле "text"
                "parse_mode": "HTML" # если нужно HTML-форматирование
            }
            r = requests.post(url=url, headers=headers, json=payload)
            if r.status_code == 200:
                task.status = 'success'
            else:
                task.status = 'failed'
                task.error_message = f"Status Code: {r.status_code}, Response: {r.text}"
                task.save()
                return

        # Случай 2: Есть фото (одно или несколько)
        else:
            # Отправляем каждую ссылку по отдельности 
            # (или дорабатываем, если хотим отправлять массив ссылок за один раз)
            send_photo_url = f"{TELEGRAM_API_URL}/api/v1/send_photo"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": TELEGRAM_API_KEY
            }
            # В JSON передаём "photo" и "massage" (у вас в коде именно 'massage', не 'message')
            payload = {
                "photos": photo_urls,
                "message": message  # подпись к фото (или caption)
            }
            resp = requests.post(url=send_photo_url, headers=headers, json=payload)
            if resp.status_code != 200:
                task.status = 'failed'
                task.error_message = f"Status Code: {resp.status_code}, Response: {resp.text}"
                task.save()
                return

            # Если все фото отправлены успешно, считаем задачу выполненной
            task.status = 'success'

    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)

    task.save()

@shared_task
def send_notification_for_selected_users(
    task_id: int,
    message: str,
    client_ids: list,
    photo_urls=None
):
    """
    Отправляем сообщение/фото конкретным пользователям, 
    у которых есть Telegram chat_id, 
    и которые перечислены в client_ids (ID в нашей БД).
    """

    from .models import NotificationTask
    from clients.models import Client
    from .config import TELEGRAM_API_KEY, TELEGRAM_API_URL

    if photo_urls is None:
        photo_urls = []

    task = NotificationTask.objects.get(id=task_id)
    task.status = 'pending'
    task.save()

    # Получаем клиентов из БД
    clients = Client.objects.filter(id__in=client_ids).exclude(telegram_chat_id__isnull=True).exclude(telegram_chat_id__exact='')

    # Если клиентов нет – можно сразу пометить задачу, что не удалось никому отправить
    if not clients.exists():
        task.status = 'failed'
        task.error_message = "Нет ни одного пользователя с chat_id среди выбранных."
        task.save()
        return

    try:
        # Пробегаемся по каждому клиенту
        for client in clients:
            chat_id = client.telegram_chat_id

            # Случай 1: Нет фото => шлём только текст
            if not photo_urls:
                url = f"{TELEGRAM_API_URL}/api/v1/send_message"
                headers = {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "X-API-Key": TELEGRAM_API_KEY
                }
                payload = {
                    "text": message,     
                    "parse_mode": "HTML",
                    "chat_id": chat_id,  # важно передать нужный chat_id
                }
                r = requests.post(url=url, headers=headers, json=payload)

                if r.status_code != 200:
                    # Не обязательно падать на одном неудачном отправлении — 
                    # можно логировать, а потом продолжать остальным.
                    # Но для простоты — прервёмся.
                    task.status = 'failed'
                    task.error_message = f"Ошибка при отправке пользователю {chat_id}: {r.text}"
                    task.save()
                    return

            else:
                # Случай 2: Есть фото
                send_photo_url = f"{TELEGRAM_API_URL}/api/v1/send_photo"
                headers = {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "X-API-Key": TELEGRAM_API_KEY
                }
                payload = {
                    "photos": photo_urls,  # список ссылок на фото
                    "message": message,
                    "chat_id": chat_id,    # конкретный получатель
                }
                resp = requests.post(url=send_photo_url, headers=headers, json=payload)
                if resp.status_code != 200:
                    task.status = 'failed'
                    task.error_message = f"Ошибка при отправке фото пользователю {chat_id}: {resp.text}"
                    task.save()
                    return

        # Если дошли сюда, значит всем пользователям успешно отправлено
        task.status = 'success'
        task.save()

    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()