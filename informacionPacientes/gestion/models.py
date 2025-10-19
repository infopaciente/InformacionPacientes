# gestion/models.py
from django.db import models
from django.utils import timezone

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Paciente(models.Model):
    # Opciones para el campo 'estado'
    ESTADO_CHOICES = [
        ('Estable', 'Estable'),
        ('Delicado', 'Delicado'),
        ('Recuperación', 'Recuperación'),
    ]

    nhc = models.CharField(max_length=20, unique=True, verbose_name="NHC") # NHC = Número de Historia Clínica (ej. HSP-1010)
    nombre = models.CharField(max_length=200)
    edad = models.PositiveIntegerField()
    area = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name="pacientes") # Clave foránea a Especialidad
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Estable')
    fecha_ingreso = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.nhc} - {self.nombre}"