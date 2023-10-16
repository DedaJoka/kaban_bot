"""
URL configuration for kaban_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('incoming/', views.incoming, name='incoming'),
    path('', views.incoming, name='incoming'),
    path('viber_bot/master_registration/<str:viber_id>/', views.master_registration_page_view, name='master_registration_page'),
    path('master_registration/registration_submit', views.master_registration_page_submit, name='master_registration/registration_submit'),
]

