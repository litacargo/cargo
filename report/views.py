from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Min, Max
from products.models import Product, Status
from datetime import date
from config.config import BaseStatus
from take.models import Payment

@login_required
def report(request):
    # Получение текущей даты
    today = date.today()

    # Получение параметров из запроса или установка текущей даты по умолчанию
    start_date = request.GET.get('start_date', today.strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))

    status, _ = Status.objects.get_or_create(name=BaseStatus.PIKED)
    # Фильтрация товаров по дате и статусу
    products = Product.objects.filter(date__range=[start_date, end_date], status=status)
    
    # Сводная информация
    total_clients = products.values('client').distinct().count()
    total_products = products.count()
    total_weight = products.aggregate(Sum('weight'))['weight__sum'] or 0
    total_price = products.aggregate(Sum('price'))['price__sum'] or 0

    # Детальная информация по клиентам с добавлением способа оплаты
    client_details = products.values(
        'client__name', 
        'client__code',
        'payments__payment_method__name'  # Добавляем способ оплаты из связанной модели Payment
    ).annotate(
        total_products=Count('id'),
        total_weight=Sum('weight'),
        total_price=Sum('price'),
        earliest_take_time=Min('take_time'),
        latest_take_time=Max('take_time')
    ).order_by('client__name')

    # Подробности по каждому товару с добавлением способа оплаты
    product_details = products.values(
        'product_code', 
        'weight', 
        'price', 
        'take_time', 
        'client__name', 
        'client__code',
        'payments__payment_method__name'  # Способ оплаты
    ).order_by('client__name', 'take_time')

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_clients': total_clients,
        'total_products': total_products,
        'total_weight': total_weight,
        'total_price': total_price,
        'client_details': client_details,
        'product_details': product_details,
        'current_page': 'report',
        'title': 'Отчет',
    }

    return render(request, 'report/report.html', context)