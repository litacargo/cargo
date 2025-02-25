from datetime import datetime
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from products.models import Product, Status
from clients.models import Client
from branch.models import Branch

from django.views import View
from django.contrib import messages

from config.views import get_user_branch
from config.config import BaseStatus

import openpyxl

from notifications.notification_china import send_notification_china
from notifications.notification_bishkek import send_notification_bihskek

class ProductListView(View):
    def get(self, request):
        # Получение параметров фильтрации
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        # Получение всех товаров
        user = request.user
        products_list = get_user_branch(user, Product).exclude(status__name=BaseStatus.PIKED).order_by('-id')

        # Фильтрация по поисковому запросу
        if search_query:
            products_list = products_list.filter(
                product_code__icontains=search_query
            ) | products_list.filter(
                status__name__icontains=search_query
            ) | products_list.filter(
                client__name__icontains=search_query
            )

        # Фильтрация по статусу
        if status_filter:
            products_list = products_list.filter(status__id=status_filter)

        # Фильтрация по дате
        if start_date:
            products_list = products_list.filter(date__gte=start_date)
        if end_date:
            products_list = products_list.filter(date__lte=end_date)

        # Пагинация
        paginator = Paginator(products_list, 30)  # 30 товаров на страницу
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Получение всех статусов для фильтрации
        statuses = Status.objects.all()

        # Рендер страницы
        return render(
            request,
            'products/products.html',
            {
                'current_page': 'products',
                'title': 'Товары',
                'page_obj': page_obj,
                'search_query': search_query,
                'status_filter': status_filter,
                'start_date': start_date,
                'end_date': end_date,
                'statuses': statuses,
                'request': request
            }
        )

    
    def edit_products_page(request):
        product_ids = request.POST.getlist('product_ids')
        products = Product.objects.filter(id__in=product_ids)
        statuses = Status.objects.all()
        return render(request, 'products/edit_products.html', {
                'products': products,
                'statuses': statuses,
                'current_page': 'products',
                'title': 'Изменить',
            })
    
    def update_products(request):
        product_ids = request.POST.getlist('product_ids')
        new_status_id = request.POST.get('status', '').strip()

        if not product_ids:
            messages.error(request, "Не выбраны товары.")
            return redirect('products')

        update_data = {"date": datetime.utcnow()}

        try:
            # Если указан новый статус
            if new_status_id:
                new_status = Status.objects.get(id=new_status_id)
                update_data["status"] = new_status

            # Проверяем, есть ли изменения
            if len(update_data) > 1:  # кроме даты должно быть хотя бы одно поле
                Product.objects.filter(id__in=product_ids).update(**update_data)
                messages.success(request, "Товары успешно обновлены.")
            else:
                messages.warning(request, "Ничего не изменено, не были указаны ни новый статус, ни филиал.")

        except Status.DoesNotExist:
            messages.error(request, "Выбранный статус не существует.")
        except Branch.DoesNotExist:
            messages.error(request, "Выбранный филиал не существует.")
        except ValueError:
            messages.error(request, "Некорректные данные для обновления товаров.")
        except Exception as e:
            messages.error(request, f"Ошибка при обновлении товаров: {e}")

        return redirect('products')
    
    def delete_products(request):
        """
        Удаление выбранных товаров с подтверждением.
        """
        if request.method == "POST" and 'confirm' in request.POST:
            # Если пользователь подтвердил удаление
            product_ids = request.POST.getlist('product_ids')
            deleted_count, _ = Product.objects.filter(id__in=product_ids).delete()
            messages.success(request, f"Удалено {deleted_count} товаров.")
            return redirect('products')  # Замените 'products' на имя URL для списка товаров

        elif request.method == "POST":
            # Первоначальный запрос на удаление — отобразить страницу подтверждения
            product_ids = request.POST.getlist('product_ids')
            if not product_ids:
                messages.error(request, "Не выбраны товары для удаления.")
                return redirect('products')

            products = Product.objects.filter(id__in=product_ids)
            return render(request, 'products/confirm_delete_products.html', {
                'products': products,
                'current_page': 'products',
                'title': 'Подтверждение удаления',
            })





@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    statuses = Status.objects.all()


    if request.method == "POST":
        # Получаем данные из POST и заменяем запятую на точку
        product_code = request.POST.get("product_code", "").strip()
        weight_str = request.POST.get("weight", "").replace(",", ".").strip()
        price_str = request.POST.get("price", "").replace(",", ".").strip()
        date_str = request.POST.get("date", "").strip()
        status_id = request.POST.get("status", "").strip()
        client_code = request.POST.get("client_code", "").strip()  # Изменено на client_code
        branch_id = request.POST.get("branch", "").strip()

        # Если поле не пустое, только тогда меняем:
        if product_code:
            product.product_code = product_code
        if weight_str:
            try:
                product.weight = Decimal(weight_str)
            except (ValueError, Decimal.InvalidOperation):
                messages.error(request, "Неверный формат веса.")
                return render(request, 'products/edit_product.html', {
                    'product': product,
                    'statuses': statuses,
                    'current_page': 'products',
                    'title': 'Изменить',
                })
        if price_str:
            try:
                product.price = int(Decimal(price_str))  # IntegerField требует целое число
            except (ValueError, Decimal.InvalidOperation):
                messages.error(request, "Неверный формат цены.")
                return render(request, 'products/edit_product.html', {
                    'product': product,
                    'statuses': statuses,
                    'current_page': 'products',
                    'title': 'Изменить',
                })
        if date_str:
            product.date = date_str
        if status_id:
            product.status_id = status_id
        if client_code:
            try:
                client = Client.objects.get(code=client_code)
                product.client = client
            except Client.DoesNotExist:
                messages.error(request, "Клиент с таким кодом не найден.")
                return render(request, 'products/edit_product.html', {
                    'product': product,
                    'statuses': statuses,
                    'current_page': 'products',
                    'title': 'Изменить',
                })
        if branch_id:
            product.branch_id = branch_id

        # Сохраняем объект
        product.save()
        messages.success(request, "Ваши изменения успешно сохранены!")
        return redirect('products')

    return render(request, 'products/edit_product.html', {
        'product': product,
        'statuses': statuses,
        'current_page': 'products',
        'title': 'Изменить',
    })


@login_required
@permission_required('products.delete_product', raise_exception=True)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect('products')  # Замените 'products' на имя URL для списка товаров

    return render(request, 'products/delete_product.html', {'product': product, 'current_page': 'products', 'title': 'Удалить',})

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Извлекаем клиента по id
    client = product.client

    return render(request, 'products/product_detail.html', {
        'product': product,
        'client': client,
        'current_page': 'products',
        'title': 'Детали',
    })


def page_china(request):
    return render(request, "products/china.html", {"title": "Китай", 'current_page': 'products'})

def add_products_china(request):
    """Обработка загрузки файла и добавления товаров"""
    if request.method == "POST":
        try:
            file = request.FILES.get('file')  # Получаем файл
            if not file:
                messages.error(request, "Файл не выбран.")
                return redirect("page_china")  # Перенаправляем на форму

            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            products_created = 0
            products_skipped = 0  # Счётчик пропущенных товаров
            clients_products_count = {}

            for row in sheet.iter_rows(min_row=2, values_only=True):  # Пропускаем заголовок
                    # Проверяем только наличие product_code
                if len(row) < 1 or not row[0]:
                    continue  # Пропустить строки без product_code

                product_code = str(row[0]).strip()
                client_id = None
                client = None

                # Проверяем, есть ли client_id во второй колонке
                if len(row) >= 2 and row[1] is not None:
                    client_id = row[1]
                    # Если client_id — число с плавающей точкой, убираем ".0"
                    if isinstance(client_id, float):
                        client_id = str(int(client_id))
                    else:
                        client_id = str(client_id).strip()

                    # Найти клиента по code
                    client = Client.objects.filter(code=client_id).first()
                    if not client:
                        messages.warning(request, f"Нету такого клиента: {client_id}")

                # Обработка даты
                if date:
                    if isinstance(date, datetime):
                        date = date.date()  # Уже datetime, просто берем date
                    elif isinstance(date, str):
                        try:
                            date = datetime.strptime(date, "%d-%m-%Y").date()  # Формат из примера: 25-10-2024
                        except ValueError:
                            try:
                                date = datetime.strptime(date, "%d.%m.%Y").date()  # Альтернатива: 25.10.2024
                            except ValueError:
                                messages.warning(request, f"Неверный формат даты для {product_code}: {date}")
                                date = None
                    else:
                        date = None

                # Получить статус "Китай"
                china_status, _ = Status.objects.get_or_create(name=BaseStatus.CHINA)

                # Проверить, существует ли уже товар с этим кодом и клиентом (если клиент есть)
                if client and Product.objects.filter(product_code=product_code, client=client).exists():
                    products_skipped += 1
                    continue
                # Если клиента нет, проверяем только по product_code
                elif not client and Product.objects.filter(product_code=product_code, client__isnull=True).exists():
                    products_skipped += 1
                    continue

                # Создать продукт
                Product.objects.create(
                    product_code=product_code,
                    client=client,  # Будет None, если client_id не указан или клиент не найден
                    date=datetime.utcnow(),
                    status=china_status,
                    branch=client.branch if client else None,  # Устанавливаем branch только если есть клиент
                )
                products_created += 1

                # Увеличиваем счетчик товаров у клиента (только если клиент есть)
                if client and client.id not in clients_products_count:
                    clients_products_count[client.id] = 0
                if client:
                    clients_products_count[client.id] += 1

            if products_created > 0:
                messages.success(request, f"Успешно создано продуктов: {products_created}")
            if products_skipped > 0:
                messages.warning(request, f"Пропущено продуктов (уже существуют): {products_skipped}")
            # Добавляем сообщение с количеством товаров по каждому клиенту
            if clients_products_count:
                send_notification_china.delay(clients_products_count)
                for client_id, count in clients_products_count.items():
                    messages.info(request, f"Клиент {client_id}: {count} товаров")

        except Exception as e:
            messages.error(request, f"Ошибка при обработке файла: {str(e)}")

        return redirect("page_china")  # Перенаправляем на форму после обработки

    return redirect("page_china")


def page_bishkek(request):
    """Отображение страницы для загрузки товаров в Бишкеке"""
    return render(request, "products/bishkek.html", {"title": "Бишкек", 'current_page': 'products'})


def add_products_bishkek(request):
    """Обработка загрузки файла и добавления/обновления товаров"""
    if request.method == "POST":
        try:
            file = request.FILES.get('file')  # Получаем файл
            if not file:
                messages.error(request, "Файл не выбран.")
                return redirect("page_bishkek")

            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            products_created = 0
            products_updated = 0
            clients_products_count = {}

            for row in sheet.iter_rows(min_row=2, values_only=True):
                # Требуем только product_code и weight
                if len(row) < 2 or not row[0] or not row[2]:
                    continue

                product_code = str(row[0]).strip()
                client_id = row[1] if len(row) > 1 else None
                weight = row[2]
                price = row[3] if len(row) > 3 else None
                # date = row[4] if len(row) > 4 else None

                client = None
                # Обработка client_id, если он указан
                if client_id:
                    if isinstance(client_id, float):
                        client_id = str(int(client_id))
                    else:
                        client_id = str(client_id).strip()
                    if client_id:  # Проверяем, что client_id не пустая строка
                        client = Client.objects.filter(code=client_id).first()
                        if not client:
                            messages.warning(request, f"Нету такого клиента: {client_id}")

                # Получить статус "Бишкек"
                bishkek_status, _ = Status.objects.get_or_create(name=BaseStatus.BISHKEK)

                # # Обработка даты
                # if date:
                #     if isinstance(date, datetime):
                #         date = date.date()  # Уже datetime, просто берем date
                #     elif isinstance(date, str):
                #         try:
                #             date = datetime.strptime(date, "%d-%m-%Y").date()  # Формат из примера: 25-10-2024
                #         except ValueError:
                #             try:
                #                 date = datetime.strptime(date, "%d.%m.%Y").date()  # Альтернатива: 25.10.2024
                #             except ValueError:
                #                 messages.warning(request, f"Неверный формат даты для {product_code}: {date}")
                #                 date = None
                #     else:
                #         date = None

                # Найти или обновить товар
                product, created = Product.objects.get_or_create(
                    product_code=product_code,
                    client=client,
                    defaults={
                        "status": bishkek_status,
                        "weight": weight,
                        # "date": date if date else datetime.now().date(),  # Используем datetime.now()
                    }
                )

                if created:
                    products_created += 1
                else:
                    product.weight = weight
                    product.status = bishkek_status
                    if price is not None:
                        product.price = price
                    # if date is not None:
                    #     product.date = date
                    product.save()
                    products_updated += 1

                # Увеличиваем счетчик товаров у клиента, только если клиент есть
                if client and client.id not in clients_products_count:
                    clients_products_count[client.id] = 0
                if client:
                    clients_products_count[client.id] += 1

            if products_created > 0:
                messages.success(request, f"Успешно создано товаров: {products_created}")
            if products_updated > 0:
                messages.info(request, f"Обновлено товаров: {products_updated}")
            
            if clients_products_count:
                send_notification_bihskek.delay(clients_products_count)
                for client_id, count in clients_products_count.items():
                    messages.info(request, f"Клиент {client_id}: {count} товаров")

        except Exception as e:
            messages.error(request, f"Ошибка при обработке файла: {str(e)}")

        return redirect("page_bishkek")

    return redirect("page_bishkek")

@login_required
def add_product(request):
    # Получаем все статусы для формы
    statuses = Status.objects.all()

    if request.method == 'POST':
        # Получаем данные из формы
        product_code = request.POST.get('product_code')
        weight = request.POST.get('weight')
        price = request.POST.get('price')
        client_code = request.POST.get('client_code')
        status_id = request.POST.get('status')  # Получаем ID статуса из формы
        
        # Проверяем обязательные поля
        if not product_code or not client_code or not status_id:
            messages.error(request, "Код товара, код клиента и статус обязательны")
            return render(request, 'products/add_product.html', {
                'statuses': statuses,
                'current_page': 'add_product',
                'title': 'Добавить товар',
            })

        # Находим клиента
        try:
            client = Client.objects.get(code=client_code)
        except Client.DoesNotExist:
            messages.error(request, "Клиент с таким кодом не найден")
            return render(request, 'products/add_product.html', {
                'statuses': statuses,
                'current_page': 'add_product',
                'title': 'Добавить товар',
            })

        # Находим статус
        try:
            status = Status.objects.get(id=status_id)
        except Status.DoesNotExist:
            messages.error(request, "Выбранный статус не существует")
            return render(request, 'products/add_product.html', {
                'statuses': statuses,
                'current_page': 'add_product',
                'title': 'Добавить товар',
            })

        # Получаем филиал пользователя
        user = request.user
        branch = get_user_branch(user, Product).first().branch if get_user_branch(user, Product).exists() else None

        # Создаем товар
        product = Product(
            product_code=product_code,
            weight=weight if weight else None,
            price=price if price else None,
            date=timezone.now().date(),
            registered_at=timezone.now(),
            status=status,  # Используем выбранный статус
            client=client,
            branch=branch
        )
        product.save()

        # Перенаправляем на страницу добавления с сообщением об успехе
        messages.success(request, "Ваши изменения успешно сохранены!")
        return redirect('products')

    # Для GET-запроса рендерим форму с доступными статусами
    return render(request, 'products/add_product.html', {
        'statuses': statuses,
        'current_page': 'add_product',
        'title': 'Добавить товар',
    })