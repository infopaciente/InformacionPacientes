# gestion/forms.py
from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    
    # Hacemos que la fecha de ingreso use un widget de tipo "date"
    fecha_ingreso = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Ingreso"
    )

    # --- NUEVO ---
    # Hacemos que la fecha de egreso (alta) también sea un widget de fecha
    # 'required=False' permite que el campo esté vacío
    fecha_egreso = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Egreso (Alta)",
        required=False 
    )

    class Meta:
        model = Paciente
        # --- MODIFICADO ---
        # Definimos TODOS los campos que aparecerán en el formulario
        fields = [
            'nhc',
            'nombre',
            'apellido', # Añadido
            'edad',
            'area',       
            'estado',     
            'fecha_ingreso',
            'doctor_asignado', # Añadido
            'diagnostico',     # Añadido
            'fecha_egreso'     # Añadido
        ]
        labels = {
            'nhc': 'NHC (N° Historia Clínica)',
            'area': 'Área',
            'apellido': 'Apellidos',
            'doctor_asignado': 'Doctor Asignado',
            'diagnostico': 'Diagnóstico (Opcional)',
            'fecha_egreso': 'Fecha de Alta (Egreso)'
        }
        
        # --- NUEVO ---
        # Añadimos widgets para darles estilo (clases de Bootstrap)
        widgets = {
            # 'diagnostico' será un área de texto más grande
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), 
            
            # Damos estilo al resto de campos
            'nhc': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'doctor_asignado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Dr. Juan Pérez'}),
        }
