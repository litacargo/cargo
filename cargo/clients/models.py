import re
from django.db import models
from branch.models import Branch
from django.db.models import Max
from simple_history.models import HistoricalRecords
# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, db_index=True, null=True)
    numeric_code = models.IntegerField(null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    telegram_chat_id = models.CharField(max_length=255, null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    branch = models.ForeignKey(Branch, related_name="clients", on_delete=models.SET_NULL, null=True, blank=True)

    history = HistoricalRecords() # Подключение истории изменений

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def save(self, *args, **kwargs):
        if not self.numeric_code:  # Генерируем числовую часть только если её нет
            # Берем максимальный numeric_code среди всех клиентов
            last_numeric = Client.objects.aggregate(Max('numeric_code'))['numeric_code__max'] or 0
            self.numeric_code = last_numeric + 1

        # Формируем code как branch.code + numeric_code
        branch_code = self.branch.code if self.branch else ''
        self.code = f"{branch_code}{self.numeric_code}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name