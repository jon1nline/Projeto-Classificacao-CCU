from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pacientes, name='lista_pacientes'),
    path('dados-coletados/', views.dados_coletados, name='dados_coletados'),
    path('novo/', views.novo_paciente, name='novo_paciente'),
    path('<int:pk>/', views.detalhes_paciente, name='detalhes_paciente'),
    path('<int:pk>/editar/', views.editar_paciente, name='editar_paciente'),
    path('<int:pk>/processar-pdf/', views.processar_pdf_exame, name='processar_pdf_exame'),
    path('<int:pk>/historico-sexual/', views.adicionar_historico_sexual, name='adicionar_historico_sexual'),
    path('<int:pk>/historico-reprodutivo/', views.adicionar_historico_reprodutivo, name='adicionar_historico_reprodutivo'),
    path('<int:pk>/vacinacao/', views.adicionar_vacinacao, name='adicionar_vacinacao'),
    path('<int:pk>/exame-dna-hpv/', views.adicionar_exame_dna_hpv, name='adicionar_exame_dna_hpv'),
    path('<int:pk>/citopatologico/', views.adicionar_citopatologico, name='adicionar_citopatologico'),
    path('<int:pk>/procedimento/', views.adicionar_procedimento, name='adicionar_procedimento'),
    path('<int:pk>/status-seguimento/', views.adicionar_status_seguimento, name='adicionar_status_seguimento'),
]
