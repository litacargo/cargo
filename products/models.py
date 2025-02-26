from django.db import models
from clients.models import Client
from config.models import Configuration
from branch.models import Branch
from decimal import Decimal
from simple_history.models import HistoricalRecords


class Status(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    history = HistoricalRecords()  # Подключение истории изменений

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name


class Product(models.Model):
    product_code = models.CharField(max_length=255, db_index=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    date = models.DateField(db_index=True)
    take_time = models.DateTimeField(null=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(Status, related_name="products", on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, related_name="products", on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    branch = models.ForeignKey(Branch, related_name="products", on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()  # Подключение истории изменений


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.product_code
    

class ProductFile(models.Model):
    file = models.FileField(upload_to='temp_products/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')  # pending, processed, failed
    error_message = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return self.file.url

    def __str__(self):
        return f"{self.file.name} (uploaded by {self.user})"