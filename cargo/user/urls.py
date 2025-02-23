from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_users, name='users'),
    path('create/', views.create_user_page, name='create_user_page'),
    path('create_user/', views.create_user, name='create_user'),
    path('delete/<int:user_id>', views.delete_user_page, name='delete_user_page'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('permissions/<int:user_id>/', views.user_permissions, name='user_permissions'),
    path('permissions/<int:user_id>', views.user_permissions, name='user_permissions'),
    path('update_user_permissions/<int:user_id>/', views.update_user_permissions, name='update_user_permissions'),
    path('user/<int:user_id>/branch-permissions/', views.user_branch_permissions, name='user_branch_permissions'),
]