import os
from celery import Celery
from celery.schedules import crontab

# Установите настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cargo.settings')

app = Celery('cargo')

app.conf.broker_connection_retry_on_startup = True

# Используем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')


# Автоматическое обнаружение задач в приложениях
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'update-product-statuses-every-minute': {
        'task': 'products.tasks.update_product_statuses',
        # 'schedule': crontab(minute='*'),  # Каждую минуту для теста
        'schedule': crontab(minute=0, hour=8), # Каждый день в 8:00
    }
}