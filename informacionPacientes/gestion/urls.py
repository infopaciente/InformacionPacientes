# gestion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Esta será la página principal después del login (ej. http://127.0.0.1:8000/)
    path('', views.dashboard, name='dashboard'),
    path('pacientes/registrar/', views.registrar_paciente, name='registrar_paciente'),
    path('pacientes/lista/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/buscar/', views.buscar_paciente, name='buscar_paciente'),
    path('hospital/croquis/', views.croquis_hospital, name='croquis_hospital'),
    path('exportar/json/', views.exportar_json, name='exportar_json'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('restablecer/', views.restablecer_datos, name='restablecer_datos'),
    path('pacientes/editar/<int:pk>/', views.editar_paciente, name='editar_paciente'),
]
