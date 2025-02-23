from django.urls import path
from . import views

urlpatterns = [
    path('', views.branch, name='branches'),
    path('add/', views.branch_create_page, name='branch_create_page'),
    path('create/', views.branch_create, name='branch_create'),
    path('delete/<int:branch_id>/', views.branch_delete, name='branch_delete'),
    path('update/<int:branch_id>/', views.branch_update, name='branch_update'),
    path('address', views.address_china, name='address')
    
]