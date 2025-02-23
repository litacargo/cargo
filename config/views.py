from django.shortcuts import get_object_or_404, render, redirect


from .models import Configuration
from branch.models import EmployeeBranchAccess
from django.contrib.auth.models import User
from take.models import PaymentMethod

from .forms import PaymentMethodForm
from django.contrib import messages

from .config import superuser_required




@superuser_required
def update_unit_price(request):
    # Получаем все параметры конфигурации
    configurations = Configuration.objects.all().order_by('-id')
    users = User.objects.all()

    return render(request, 'config/config.html', {
        'configurations': configurations,
        'users': users,
        'current_page': 'config',
        'current_mini_page': 'config', 
        'title': 'Настройки',
    })

@superuser_required
def edit_config(request, config_id):
    config = get_object_or_404(Configuration, id=config_id)

    if request.method == 'POST':
        new_value = request.POST.get('new_value')
        if new_value:
            config.value = new_value
            config.save()
            return redirect('config')  # Перенаправление на страницу списка параметров после сохранения

    return render(request, 'config/edit_config.html', {
        'config': config,
        'current_page': 'config',
        'title': 'Редактирование параметра',
    })


def get_user_branch(user, Model):
    if user.is_superuser:
       return Model.objects.all().order_by('-registered_at')
    access = EmployeeBranchAccess.objects.filter(user=user).first()
    if not access:
        return Model.objects.none()
    
    model = access.branches.all()
    return Model.objects.filter(branch__in=model)

@superuser_required
def payment_method(request):
    payment_methods = PaymentMethod.objects.all().order_by('name')
    return render(request, 'payment/payment.html', {
        'payment_methods': payment_methods,
        'current_page': 'config',
        'current_mini_page': 'payment_methods',
        'title': 'Способы оплаты',
    })

# Создание способа оплаты (Create)
@superuser_required
def payment_method_create(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Способ оплаты успешно создан!')
            return redirect('payment_method_list')
    else:
        form = PaymentMethodForm()
    return render(request, 'payment/form.html', {
        'form': form,
        'title': 'Добавить способ оплаты',
        'current_mini_page': 'payment_methods',
        'current_page': 'config',

    })

@superuser_required
def payment_method_update(request, pk):
    payment_method = get_object_or_404(PaymentMethod, pk=pk)
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            form.save()
            messages.success(request, 'Способ оплаты успешно обновлён!')
            return redirect('payment_method_list')
    else:
        form = PaymentMethodForm(instance=payment_method)
    return render(request, 'payment/form.html', {
        'form': form,
        'title': 'Редактировать способ оплаты',
        'current_mini_page': 'payment_methods',
        'current_page': 'config',
    })