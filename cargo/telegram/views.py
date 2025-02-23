from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from .task import send_nottification_for_all_users, send_notification_for_selected_users
from django.contrib import messages
from .models import NotificationTask, NotificationImage

# Create your views here.
def telegram_tasks(request):
    tasks = NotificationTask.objects.all().order_by('-created_at')
    return render(
        request, 
        'telegram/telegram.html',
        {
            'current_mini_page': 'telegram',
            'current_page': 'telegram',
            'title': 'Телеграм',
            'tasks': tasks,
        }
    )

def telegram_notifications_page(request):
    
    return render(
        request, 
        'telegram/telegram_notifications.html',
        {   
            'current_page': 'telegram',
            'current_mini_page': 'telegram_notifications',
            'title': 'Уведомления Телеграм',
        }
    )

@csrf_exempt
def send_notifications(request):
    if request.method == "POST":
        send_type = request.POST.get('send_type', 'all')  # "all" или "selected"

        message = request.POST.get('message', '').strip()
        images = request.FILES.getlist('images')

        if not message and len(images) == 0:
            messages.warning(request, "Нужно ввести текст сообщения или выбрать фото (или и то, и другое).")
            return redirect("telegram_notifications")

        # Создаём задачу
        task = NotificationTask.objects.create(
            message=message,
            status='pending'
        )

        # Сохраним изображения
        image_urls = []
        try:
            for img in images:
                notification_image = NotificationImage.objects.create(task=task, image=img)
                full_image_url = request.build_absolute_uri(notification_image.image.url)
                image_urls.append(full_image_url)
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            messages.error(request, f"Ошибка при сохранении изображений: {e}")
            return redirect("telegram_notifications")

        # Если хотим запомнить, кому отправляем (для отображения в админке, например)
        if send_type == 'all':
            # Вызываем таску для отправки всем
            try:
                send_nottification_for_all_users.delay(task.id, message, image_urls)
                messages.success(request, "Задача на отправку ВСЕМ пользователям создана.")
            except Exception as e:
                task.status = 'failed'
                task.error_message = str(e)
                task.save()
                messages.error(request, f"Ошибка при отправке задачи: {e}")

        else:
            # Получаем список ID клиентов
            selected_client_ids = request.POST.getlist('selected_clients')
            if not selected_client_ids:
                messages.warning(request, "Не выбраны пользователи для отправки.")
                task.delete()  # удаляем задачу, т.к. бессмысленно
                return redirect("telegram_notifications")

            # Сохраняем в БД (чтобы потом видно было в админке) — не обязательно
            task.recipients.set(selected_client_ids)

            # Запускаем Celery задачу
            try:
                send_notification_for_selected_users.delay(
                    task.id, 
                    message, 
                    client_ids=selected_client_ids, 
                    photo_urls=image_urls
                )
                messages.success(request, "Задача на отправку выбранным пользователям создана.")
            except Exception as e:
                task.status = 'failed'
                task.error_message = str(e)
                task.save()
                messages.error(request, f"Ошибка при отправке задачи: {e}")

        return redirect("telegram_notifications")

    # Если GET — редирект
    return redirect("telegram_notifications")