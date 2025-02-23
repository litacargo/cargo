from django.contrib import admin
from .models import NotificationTask, NotificationImage
# Register your models here.

@admin.register(NotificationTask)
class NotificationTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at')

@admin.register(NotificationImage)
class NotificationImageAdmin(admin.ModelAdmin):
    pass