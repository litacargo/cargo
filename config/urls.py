from django.urls import path
from . import views

urlpatterns = [
    path('', views.update_unit_price, name='config'),
    path('edit/<int:config_id>/', views.edit_config, name='edit_config'),

    path('payment/', views.payment_method, name='payment_method_list'),   
    path('payment/create/', views.payment_method_create, name='payment_method_create'),
    path('payment/<int:pk>/update/', views.payment_method_update, name='payment_method_update'),
]