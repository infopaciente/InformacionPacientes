# gestion/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # Necesario para el doctor

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
        ('De Alta', 'De Alta'), # Añadimos 'De Alta'
    ]

    nhc = models.CharField(max_length=20, unique=True, verbose_name="NHC")
    
    # --- CAMBIO IMPORTANTE ---
    # Separamos nombre y apellido para que coincida con tu lógica
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100) 
    
    edad = models.PositiveIntegerField()
    area = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name="pacientes")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Estable')
    fecha_ingreso = models.DateField(default=timezone.now)

    # --- CAMPOS NUEVOS DE TU LISTA ---
    # 1. Doctor Asignado
    doctor_asignado = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doctor Asignado")
    
    # 2. Diagnóstico (Oculto)
    diagnostico = models.TextField(blank=True, null=True, verbose_name="Diagnóstico")
    
    # 3. Alta (Egreso)
    fecha_egreso = models.DateField(blank=True, null=True, verbose_name="Fecha de Egreso")

    def __str__(self):
        # Actualizamos esto para mostrar el nombre completo
        return f"{self.nhc} - {self.nombre} {self.apellido}"


# --- ¡NUEVO MODELO DE VISITAS! ---

class Visita(models.Model):
    # El paciente que está siendo visitado.
    # Si se borra el paciente, se borran sus visitas (models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="visitas")
    
    # Información del visitante
    nombre_visitante = models.CharField(max_length=200, verbose_name="Nombre del Visitante")
    dni_visitante = models.CharField(max_length=20, verbose_name="DNI del Visitante")
    
    # Horas
    hora_ingreso = models.DateTimeField(default=timezone.now, verbose_name="Hora de Ingreso")
    
    # La hora de salida puede estar vacía (mientras la visita está activa)
    hora_salida = models.DateTimeField(blank=True, null=True, verbose_name="Hora de Salida")

    def __str__(self):
        return f"Visita de {self.nombre_visitante} a {self.paciente.nombre}"
    
    # Para saber si la visita sigue activa
    @property
    def activa(self):
        return self.hora_salida is None
