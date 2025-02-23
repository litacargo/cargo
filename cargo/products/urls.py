from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='products'),
    path('eidt/', views.ProductListView.edit_products_page, name='edit_products_page'),
    path('update/confirm/', views.ProductListView.update_products, name='update_products'),
    path('delete/', views.ProductListView.delete_products, name='delete_products'),

    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('detail/<int:product_id>/', views.product_detail, name='product_detail'),


    path('china/', views.page_china, name="page_china"),
    path('china/upload/', views.add_products_china, name="add_products_china"),

    path('bishkek/', views.page_bishkek, name="page_bishkek"),
    path('bishkek/upload/', views.add_products_bishkek, name="add_products_bishkek"),

    path('add/', views.add_product, name='add_product'),
]