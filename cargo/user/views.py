from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.contrib.auth.models import User

from config.config import superuser_required
from .forms import CustomUserCreationForm
from branch.models import Branch, EmployeeBranchAccess

# Create your views here.

@superuser_required
def get_users(request):
    users = User.objects.all()
    return render(request, 'user/users.html', 
        {
            'users': users, 
            'current_page': 'config',
            'current_mini_page': 'users', 
            'title': 'Пользователи'
        }
    )

def create_user_page(request):
    return render(request, 'user/create_user.html', {
        'current_page': 'config',
        'title': 'Создание пользователя',
    })

def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users')  # Редирект на список пользователей, например
    else:
        form = CustomUserCreationForm()

    return render(request, 'user/create_user.html', {
        'form': form,
        'current_page': 'config',
        'title': 'Создание пользователя',
    })



def delete_user_page(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'user/delete_user.html', {
        'user': user,
        'current_page': 'config',
        'title': 'Удаление пользователя',
    })


def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('users')


def user_permissions(request, user_id):
    edit_user = get_object_or_404(User, id=user_id)
    return render(request, 'user/user_permissions.html', {
        'edit_user': edit_user,
        'current_page': 'config',
        'title': 'Права пользователя',
    })

def update_user_permissions(request, user_id):
    edit_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        edit_user.first_name = request.POST.get('first_name')
        edit_user.last_name = request.POST.get('last_name')
        edit_user.email = request.POST.get('email')
        edit_user.is_active = 'is_active' in request.POST
        edit_user.is_staff = 'is_staff' in request.POST
        edit_user.is_superuser = 'is_superuser' in request.POST
        password = request.POST.get('password')
        if password:
            edit_user.set_password(password)
        edit_user.save()
        return redirect('users')

    return render(request, 'user/update_user_permissions.html', {
        'current_page': 'config',
        'title': 'Обновление прав пользователя',
        'message': 'Права пользователя успешно обновлены' if request.method == 'POST' else ''
    })

@login_required
def user_branch_permissions(request, user_id):
    edit_user = get_object_or_404(User, id=user_id)

    # Получаем или создаем доступ пользователя к филиалам
    access, created = EmployeeBranchAccess.objects.get_or_create(user=edit_user)

    if request.method == 'POST':
        # Получаем список выбранных филиалов из POST-запроса
        selected_branch_ids = request.POST.getlist('branches')
        selected_branches = Branch.objects.filter(id__in=selected_branch_ids)

        # Обновляем доступ пользователя
        access.branches.set(selected_branches)

        return HttpResponseRedirect(request.path_info)

    # Передаем в шаблон
    return render(request, 'user/user_branch_permissions.html', {
        'edit_user': edit_user,
        'branches': Branch.objects.all(),
        'user_branches': access.branches.all(),
        'current_page': 'config',
        'title': 'Права пользователя на филиалы',
    })