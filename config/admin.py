from django.contrib import admin
from .models import Configuration
# Register your models here.

@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'name')
    list_editable = ('value',)
    ordering = ('key',)