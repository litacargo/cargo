from django.urls import path
from . import views

urlpatterns = [
    path('', views.take, name='take'),
]