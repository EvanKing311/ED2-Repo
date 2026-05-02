from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('MatlabApp.urls')),   #root goes to app
    path('', lambda request: redirect('login')),
]
