from django.urls import path
from . import views

urlpatterns = [
    path('', views.telegram_notifications_page, name='telegram_notifications'),
    path('tasks/', views.telegram_tasks, name='telegram_tasks'),
    path('send/notifications/', views.send_notifications, name='send_notifications'),
]