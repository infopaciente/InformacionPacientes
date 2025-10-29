# gestion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Esta será la página principal después del login (ej. http://127.0.0.1:8000/)
    path('', views.dashboard, name='dashboard'),
    path('pacientes/registrar/', views.registrar_paciente, name='registrar_paciente'),
    path('pacientes/lista/', views.lista_pacientes, name='lista_pacientes'),
    
    # --- MODIFICADO ---
    # Reemplazamos la URL de buscar vieja por la nueva que busca por DNI
    path('pacientes/buscar/dni/', views.buscar_paciente_dni, name='buscar_paciente_dni'), 
    
    path('hospital/croquis/', views.croquis_hospital, name='croquis_hospital'),
    
    # --- NUEVA URL ---
    # URL para ver el detalle de un paciente
    path('pacientes/ver/<int:id>/', views.ver_paciente, name='ver_paciente'), 
    
    # --- MODIFICADO ---
    # URL para editar (cambiamos pk por id para que coincida con views.py)
    path('pacientes/editar/<int:id>/', views.editar_paciente, name='editar_paciente'), 
    
    # --- NUEVA URL ---
    # URL para eliminar un paciente
    path('pacientes/eliminar/<int:id>/', views.eliminar_paciente, name='eliminar_paciente'), 
    
    # URLs de exportación y restablecimiento
    path('exportar/json/', views.exportar_json, name='exportar_json'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('restablecer/', views.restablecer_datos, name='restablecer_datos'),
    
    # La URL original 'pacientes/buscar/' (views.buscar_paciente) se elimina 
    # porque la función 'buscar_paciente' ya no existe en nuestro nuevo 'views.py'
]
