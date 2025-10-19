# gestion/migrations/XXXX_poblar_especialidades.py
from django.db import migrations

ESPECIALIDADES_LISTA = [
    "Medicina General", "Cardiología", "Neurología",
    "Gastroenterología", "Neumología", "Hematología",
    "Cirugía General", "Traumatología", "Endocrinología"
]

def poblar_datos(apps, schema_editor):
    Especialidad = apps.get_model('gestion', 'Especialidad')
    for nombre in ESPECIALIDADES_LISTA:
        Especialidad.objects.get_or_create(nombre=nombre)

class Migration(migrations.Migration):

    # Asegúrate que '0001_initial' es tu migración anterior
    dependencies = [
        ('gestion', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(poblar_datos),
    ]