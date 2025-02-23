from django.db import models
from products.models import Product
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from branch.models import Branch
from clients.models import Client

# Create your models here.
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название способа оплаты")
    code = models.CharField(max_length=20, unique=True, verbose_name="Код способа оплаты")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Способ оплаты'
        verbose_name_plural = 'Способы оплаты'

    def __str__(self):
        return self.name
    

class Payment(models.Model):
    products = models.ManyToManyField(Product, related_name="payments", blank=True)
    client = models.ForeignKey(Client, related_name="payments", on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, related_name="payments", on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, related_name="payments", on_delete=models.SET_NULL, null=True, verbose_name="Способ оплаты")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Сумма оплаты")
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name="Время оплаты")
    taken_by = models.ForeignKey(User, related_name="payments", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кто выдал")
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'

    def __str__(self):
        return f"{self.client.code if self.client else 'Без клиента'} - {self.payment_method.name if self.payment_method else 'Не указан'} - {self.paid_at}"