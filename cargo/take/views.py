from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages

from products.models import Status, Product
from clients.models import Client
from django.db.models import Q
from config.config import BaseStatus
from config.views import get_user_branch
from .models import PaymentMethod, Payment


# Create your views here.

@login_required
def take(request):
    client = None
    products = None
    total_weight = 0
    total_price = 0
    total_count = 0
    status_bishkek = get_object_or_404(Status, name=BaseStatus.BISHKEK)
    status_zabrali = get_object_or_404(Status, name=BaseStatus.PIKED)
    
    client_code = request.GET.get('client_code', '')
    
    if client_code:
        try:
            client = Client.objects.get(code=client_code)
            user = request.user
            products = get_user_branch(user, Product).filter(
                status=status_bishkek,
                client=client
            )
            total_weight = products.aggregate(total_weight=Sum('weight'))['total_weight'] or 0
            total_price = products.aggregate(total_price=Sum('price'))['total_price'] or 0
            total_count = products.count()
        except Client.DoesNotExist:
            messages.warning(request, f"Клиент с кодом '{client_code}' не найден.")

    if request.method == 'POST':
        selected_products = request.POST.getlist('selected_products')
        payment_method_id = request.POST.get('payment_method')  # Получаем ID способа оплаты

        if selected_products and payment_method_id:
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
                products_to_update = Product.objects.filter(id__in=selected_products)
                products_to_update.update(status=status_zabrali, date=timezone.now(), take_time=timezone.now())

                payment = Payment.objects.create(
                    client=client,
                    branch=client.branch if client else None,
                    payment_method=payment_method,
                    amount=total_price,
                    taken_by=request.user
                )
                payment.products.set(products_to_update)

                messages.success(request, "Товары успешно выданы и оплата зафиксирована!")
                return redirect(f'/take/?client_code={client_code}')
            except PaymentMethod.DoesNotExist:
                messages.error(request, "Выбранный способ оплаты недоступен!")
        else:
            messages.error(request, "Выберите товары и способ оплаты!")

    # Получаем активные способы оплаты
    payment_methods = PaymentMethod.objects.filter(is_active=True)

    return render(
        request,
        'take/take.html',
        {
            'client': client,
            'products': products,
            'client_code': client_code,
            'total_weight': total_weight,
            'total_price': total_price,
            'total_count': total_count,
            'current_page': 'take',
            'title': 'Выдать',
            'payment_methods': payment_methods,  # Передаём объекты PaymentMethod
        }
    )