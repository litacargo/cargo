from django.shortcuts import render, redirect, get_object_or_404
from .models import Branch, ChinaAddress
from django.contrib import messages
from .forms import ChinaAddressForm
from django.urls import reverse


# Create your views here.
def branch(request):
    branches = Branch.objects.all().order_by('-id')
    return render(
        request, 'branch/branch.html',
        {
            'current_page': 'config',
            'current_mini_page': 'branch',
            'title': 'Филиалы', 
            'branches': branches,
        }
    )

def branch_create_page(request):
    return render(
        request, 'branch/branch_create.html',
        {
            'current_page': 'config',
            'current_mini_page': 'branch',
            'title': 'Добавить филиал',
        }
    )
def branch_create(request):
    if request.method == "POST":
        try:
            branch = Branch.objects.create(
                name=request.POST.get("name"),
                code=request.POST.get("code"),
                address=request.POST.get("address"),
            )
            messages.success(request, "Клиент успешно добавлен.")
            return redirect('branches')  
        except:
            messages.error(request, "Ошибка добавления филиала.")
            return redirect('branch_create_page')


def branch_update(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == "POST":
        branch.name = request.POST.get("name")
        branch.code = request.POST.get("code")
        branch.address = request.POST.get("address")
        branch.save()
        return redirect('branches')
    return render(
        request, 'branch/branch_edit.html',
        {
            'branch': branch,
            'current_page': 'config',
            'current_mini_page': 'branch',
            'title': 'Обновить филиал',
        }
    )


def branch_delete(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if branch.clients.count() > 0 and branch.products.count() > 0:
        return render(
            request, 'branch/branch_delete.html',
            {
                'branch': branch,
                'current_page': 'config',
                'current_mini_page': 'branch',
                'title': 'Удалить филиал',
                'error_message': "Нельзя удалить филиал, у которого есть клиенты и товары.",
            }
        )
    elif branch.clients.count() > 0:
        return render(
            request, 'branch/branch_delete.html',
            {
                'branch': branch,
                'current_page': 'config',
                'current_mini_page': 'branch',
                'title': 'Удалить филиал',
                'error_message': "Нельзя удалить филиал, у которого есть клиенты.",
            }
        )
    
    elif branch.products.count() > 0:
        return render(
            request, 'branch/branch_delete.html',
            {
                'branch': branch,
                'current_page': 'config',
                'current_mini_page': 'branch',
                'title': 'Удалить филиал',
                'error_message': "Нельзя удалить филиал, у которого есть товары.",
            }
        )
    else:
        branch.delete()
        messages.success(request, "Филиал удален.")
    return redirect('branches')

def address_china(request):
    address = get_object_or_404(ChinaAddress, pk=1)

    if request.method == 'POST':
        form = ChinaAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            # Редирект, чтобы избежать повторной отправки формы, 
            # а также обновить отображение
            return redirect(reverse('address'))
    else:
        form = ChinaAddressForm(instance=address)

    context = {
        'address': address,
        'form': form,
        'current_page': 'config',
        'current_mini_page': 'address',
        'title': 'Адрес китай',
    }
    return render(request, 'branch/address.html', context)
