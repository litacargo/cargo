from django.contrib import admin
from .models import Client
# Register your models here.

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'number', 'city', 'telegram_chat_id', 'registered_at')
    search_fields = ('name', 'number', 'city')
    ordering = ('-registered_at',)