from django.contrib import admin
from .models import Payment, PaymentMethod
# Register your models here.

@admin.register(PaymentMethod)
class PaymentMethod(admin.ModelAdmin):
    pass

@admin.register(Payment)
class Payment(admin.ModelAdmin):
    pass