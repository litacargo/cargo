from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Client
from products.models import Product, Status, Branch
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q


from config.views import get_user_branch


# Create your views here.

@login_required
def clients(request):
    search_query = request.GET.get('search', '')

    user = request.user
    clients_list = get_user_branch(user, Client)

    # Фильтрация клиентов по имени или городу
    if search_query:
        clients_list = clients_list.filter(name__icontains=search_query) | clients_list.filter(number__icontains=search_query) | clients_list.filter(code__icontains=search_query)

    # Пагинация
    paginator = Paginator(clients_list, 30)  # 30 клиентов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  

    return render(
        request,
        'clients/clients.html',
        {
            'current_page': 'clients',
            'title': 'Клиенты',
            'page_obj': page_obj,
            'search_query': search_query,
        }
    )

@login_required
def edit_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    branches = Branch.objects.all()
    
    if request.method == "POST":
        client.name = request.POST.get("name")
        client.number = request.POST.get("number")
        client.city = request.POST.get("city")
        client.telegram_chat_id = request.POST.get("telegram_chat_id")
        branch_id = request.POST.get("branch", "").strip()
        branch = get_object_or_404(Branch, id=branch_id)
        client.branch = branch
        client.save()
        return redirect('clients_list')  # Замените 'clients_list' на имя URL для списка клиентов

    return render(request, 'clients/edit_client.html', {'client': client, 'current_page': 'clients', 'branches': branches, 'title': 'Изменить'})

@login_required
def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    # Проверка на наличие связанных товаров
    if client.products.exists():
        # Если у клиента есть товары, выводим ошибку
        return render(request, 'clients/delete_client.html', {
            'client': client,
            'error_message': 'Невозможно удалить клиента, так как у него есть товары.'
        })

    if request.method == "POST":
        client.delete()
        return redirect('clients_list')  # Замените 'clients_list' на имя URL для списка клиентов

    return render(request, 'clients/delete_client.html', {'client': client,  'current_page': 'clients', 'title': 'Удалить',})


# @login_required
# def client_detail(request, client_id):
#     client = get_object_or_404(Client, id=client_id)  # Извлекаем клиента по id
#     products = client.products.exclude(status__name="Забрали")

#     return render(request, 'clients/client_detail.html', {
#         'client': client,
#         'products': products,
#         'current_page': 'clients',
#         'title': 'Детали',
#     })

@login_required
def client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)  # Извлекаем клиента по id
    products = client.products.all().order_by('-date')  # Получаем все товары, связанные с этим клиентом, отсортированные по дате (новые в начале)

    return render(request, 'clients/client_detail.html', {
        'client': client,
        'products': products,
        'current_page': 'clients',
        'title': 'Детали',
    })

def add_client_page(request):
    branches = Branch.objects.all()
    return render(
        request,
        'clients/add_client.html',
        {
            'current_page': 'clients',
            'title': 'Добавить',
            'branches': branches,
        }
    )

def create_client(request):
    if request.method == "POST":
        try:
            branch = get_object_or_404(Branch, id=request.POST.get("branch"))

            client = Client.objects.create(
                name=request.POST.get("name"),
                number=request.POST.get("number"),
                city=request.POST.get("city"),
                telegram_chat_id=request.POST.get("telegram_chat_id"),
                branch=branch
            )

            messages.success(request, "Клиент успешно добавлен.")
            return redirect('clients_list')  

        except Exception as e:
            messages.error(request, f"Ошибка: {e}")
            return redirect('add_client')

    return redirect('add_client')


def search_clients(request):
    # Параметр, который мы ожидаем из GET-запроса, 
    # например /clients/search/?search=Иван
    search_query = request.GET.get('search', '').strip()

    # Если запрос пустой — возвращаем пустой список (или все, по вашему желанию)
    if not search_query:
        return JsonResponse([], safe=False)

    # Фильтруем клиентов по нескольким полям (name, number, city и т.д.)
    clients = Client.objects.filter(
        Q(name__icontains=search_query) |
        Q(number__icontains=search_query) |
        Q(city__icontains=search_query)
        # при желании добавляйте дополнительные условия:
        # Q(code__icontains=search_query) | ...
    )

    # Чтобы не вываливать слишком много записей, 
    # можно ограничить, например, 50 первыми результатами
    clients = clients[:50]

    # Готовим список для JSON-ответа
    results = []
    for c in clients:
        results.append({
            'id': c.id,
            'name': c.name or '',
            'number': c.number or '',
            'code': c.code or '',
            # добавляйте, что нужно
        })

    # Возвращаем JSON-список (safe=False, т.к. передаём список, а не словарь)
    return JsonResponse(results, safe=False)
