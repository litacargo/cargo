from django.urls import path
from . import views

urlpatterns = [
    path('', views.clients, name='clients_list'),
    path('edit/<int:client_id>/', views.edit_client, name='edit_client'),
    path('delete/<int:client_id>/', views.delete_client, name='delete_client'),
    path('client/<int:client_id>/', views.client_detail, name='client_detail'),
    path('add/', views.add_client_page, name='add_client'),
    path('create/', views.create_client, name='create_client'),
    path('search/', views.search_clients, name='search_clients')
]