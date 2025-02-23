
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.http import HttpResponseForbidden

def superuser_required(view_func):
    """Декоратор для ограничения доступа только суперпользователям."""
    def check_superuser(user):
        if user.is_superuser:
            return True
        return False

    def wrapper(request, *args, **kwargs):
        if not check_superuser(request.user):
            return HttpResponseForbidden(render(request, '403.html'))
        return view_func(request, *args, **kwargs)

    return wrapper


class BaseStatus:
    BISHKEK = "Можно забрать"
    CHINA = "В китае"
    TRANSIT = "В пути"
    PIKED = "Забрали"