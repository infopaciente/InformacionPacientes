"""
URL configuration for informacionPacientes project.

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
# informacionPacientes/urls.py
# informacionPacientes/urls.py

from django.contrib import admin
from django.urls import path, include

# Importamos las vistas de autenticación de Django (para el login)
from django.contrib.auth import views as auth_views 

# Importamos nuestras propias vistas de 'gestion' (para el logout)
from gestion import views as gestion_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # La vista de Login se queda como está
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    
    # Usamos nuestra vista personalizada para el Logout
    path('logout/', gestion_views.logout_view, name='logout'), 
    
    # Incluimos todas las URLs de nuestra app (dashboard, registrar, etc.)
    path('', include('gestion.urls')), 
]