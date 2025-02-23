from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('clients/', include('clients.urls')),
    path('products/', include('products.urls')),
    path('take/', include('take.urls')),
    path('report/', include('report.urls')),
    path('config/', include('config.urls')),
    path('users/', include('user.urls')),
    path('telegram/', include('telegram.urls')),
    path('branch/', include('branch.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
