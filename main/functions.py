from django.shortcuts import render
from django.db.models import Sum, Count
from products.models import Product, Status
from datetime import date
from config.config import BaseStatus


def report():
    # Получение текущей даты
    today = date.today()

    # Получение параметров из запроса или установка текущей даты по умолчанию
    start_date = today.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    status, _ = Status.objects.get_or_create(name=BaseStatus.PIKED)
    # Фильтрация товаров по дате
    products = Product.objects.filter(date__range=[start_date, end_date], status=status)
    
    # Сводная информация
    total_clients = products.values('client').distinct().count()
    total_products = products.count()
    total_weight = products.aggregate(Sum('weight'))['weight__sum'] or 0
    total_price = products.aggregate(Sum('price'))['price__sum'] or 0

    report = {
        'total_clients': total_clients,
        'total_products': total_products,
        'total_weight': total_weight,
        'total_price': total_price,
    }

    return report

    