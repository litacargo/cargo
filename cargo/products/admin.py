from django.contrib import admin
from .models import Product, Status

# Register your models here.
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_code', 'price', 'status', 'branch__code', 'date')
    search_fields = ('product_code', 'client__name')
    list_filter = ('status', 'date', 'client')
    ordering = ('-date',)