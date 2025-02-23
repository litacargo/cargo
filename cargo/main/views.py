from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .functions import report

from clients.models import Client
from products.models import Product, Status
from config.config import BaseStatus


@login_required
def index(request):
    clients_count = Client.objects.count()
    china_status = Status.objects.filter(name=BaseStatus.CHINA).first()
    bishkek_status = Status.objects.filter(name=BaseStatus.BISHKEK).first()
    transit_status = Status.objects.filter(name=BaseStatus.TRANSIT).first()
    piked_status = Status.objects.filter(name=BaseStatus.PIKED).first()

    products = {
        "count": Product.objects.count(),
        "china": Product.objects.filter(status=china_status).count(),
        "bishkek": Product.objects.filter(status=bishkek_status).count(),
        "transit": Product.objects.filter(status=transit_status).count(),
        "piked": Product.objects.filter(status=piked_status).count()
    }

    r = report()
    return render(
        request, 
        'index.html', {
            "current_page": "home",
            "title": "Главная",
            "clients_count": clients_count,
            "products": products,
            "report": r,
            }
        )

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "redirect_url": "/"})  # успешный вход
        else:
            return JsonResponse({"success": False, "error": "Неверное имя пользователя или пароль."})
    
    return render(request, 'auth/login.html')



def logout_view(request):
    logout(request)
    return redirect('login')