from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),  # Путь для входа
    path('logout/', views.logout_view, name='logout'),  # Путь для выхода
]