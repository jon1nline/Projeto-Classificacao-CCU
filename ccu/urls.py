"""
URL configuration for ccu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from feedIA.views import (
    feedback_form, treinar_ner, extrair_entidades, 
    classificar_texto, estatisticas_ner
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('pacientes/', include('pacientes.urls')),
    path('alimentar/', feedback_form, name='feedback_form'),
    path('alimentar/treinar-ner/', treinar_ner, name='treinar_ner'),
    path('alimentar/extrair-entidades/', extrair_entidades, name='extrair_entidades'),
    path('alimentar/classificar-texto/', classificar_texto, name='classificar_texto'),
    path('alimentar/estatisticas-ner/', estatisticas_ner, name='estatisticas_ner'),
]
