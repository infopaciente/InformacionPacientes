# gestion/forms.py
from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    
    # Hacemos que la fecha de ingreso use un widget de tipo "date"
    fecha_ingreso = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de Ingreso"
    )

    class Meta:
        model = Paciente
        # Definimos los campos que aparecerán en el formulario
        fields = [
            'nhc',
            'nombre',
            'edad',
            'area',       # Django lo convertirá en un <select> con las especialidades
            'estado',     # Django lo convertirá en un <select> con las opciones
            'fecha_ingreso'
        ]
        labels = {
            'nhc': 'NHC (N° Historia Clínica)',
            'area': 'Área',
        }