# gestion/admin.py
from django.contrib import admin
from .models import Especialidad, Paciente

# Estas líneas le dicen a Django que muestre
# estos modelos en el panel de admin.
admin.site.register(Especialidad)
admin.site.register(Paciente)