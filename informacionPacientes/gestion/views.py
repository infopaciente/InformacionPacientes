# gestion/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Importamos el decorador
from .models import Paciente
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib import messages # Para mostrar mensajes de éxito
from .forms import PacienteForm
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from .utils import render_to_pdf # Nuestra función
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect


# Usamos el decorador para proteger esta vista
@login_required 
def dashboard(request):
    # Datos que ya tenías
    total_pacientes = Paciente.objects.count()
    pacientes_recientes = Paciente.objects.order_by('-fecha_ingreso')[:5]
    
    # Datos para el gráfico (esta consulta ya la tenías)
    distribucion = Paciente.objects.values('area__nombre').annotate(total=Count('id')).order_by('area__nombre')

    # --- INICIO DE LA MODIFICACIÓN ---
    # Procesamos los datos para Chart.js
    chart_labels = []
    chart_data = []
    
    for item in distribucion:
        chart_labels.append(item['area__nombre'])
        chart_data.append(item['total'])
    # --- FIN DE LA MODIFICACIÓN ---

    # Pasamos los datos al template
    context = {
        'total_pacientes': total_pacientes,
        'pacientes_recientes': pacientes_recientes,
        'distribucion_data': distribucion, # La dejamos por si la usas en otro lado
        
        # --- NUEVOS DATOS PARA EL GRÁFICO ---
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'gestion/dashboard.html', context)


#REGISTRO DE PACIENTES
@login_required
def registrar_paciente(request):
    if request.method == 'POST':
        # Si el formulario se envió (POST), procesa los datos
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save() # Guarda el nuevo paciente en la BD
            messages.success(request, '¡Paciente registrado exitosamente!')
            return redirect('dashboard') # Redirige al dashboard (o a la lista de pacientes)
        else:
            # Si el formulario no es válido, muestra los errores
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        # Si es un GET, solo muestra el formulario vacío
        form = PacienteForm()

    context = {
        'form': form
    }
    return render(request, 'gestion/registrar_paciente.html', context)


# LISTAR PACIENTES
@login_required
def lista_pacientes(request):
    
    # 1. Obtenemos el término de búsqueda de la URL (ej: ?q=Juan)
    query = request.GET.get('q')
    
    # 2. Empezamos con todos los pacientes
    pacientes_list = Paciente.objects.all()
    
    # 3. Si hay un término de búsqueda, filtramos
    if query:
        # Usamos Q() para buscar en múltiples campos (OR)
        # __icontains = "contiene" (ignora mayúsculas/minúsculas)
        pacientes_list = pacientes_list.filter(
            Q(nhc__icontains=query) | 
            Q(nombre__icontains=query)
        )
    
    # 4. Ordenamos el resultado
    pacientes_list = pacientes_list.order_by('nombre')
    
    context = {
        'pacientes_list': pacientes_list,
        'query': query  # Pasamos el término de búsqueda de vuelta al template
    }
    return render(request, 'gestion/lista_pacientes.html', context)

# BUSCAR PACIENTE
@login_required
def buscar_paciente(request):
    # Esta vista solo muestra el template con el formulario de búsqueda
    return render(request, 'gestion/buscar_paciente.html')

# CROQUIS DEL HOSPITAL
@login_required
def croquis_hospital(request):
    # Esta vista solo renderiza el template del croquis
    return render(request, 'gestion/croquis_hospital.html')

# EXPORTAR DATOS A JSON
@login_required
def exportar_json(request):
    # 1. Obtenemos los datos. Usamos .values() para obtener diccionarios
    # Incluimos 'area__nombre' para obtener el *nombre* de la especialidad, no su ID.
    pacientes_queryset = Paciente.objects.all().values(
        'nhc', 
        'nombre', 
        'edad', 
        'area__nombre', 
        'estado', 
        'fecha_ingreso'
    )
    
    # 2. Convertimos el QuerySet a una lista estándar
    pacientes_lista = list(pacientes_queryset)
    
    # 3. Creamos la respuesta JSON
    # safe=False es necesario para permitir que la respuesta sea una lista.
    response = JsonResponse(pacientes_lista, safe=False)
    
    # 4. Añadimos el encabezado para forzar la descarga
    response['Content-Disposition'] = 'attachment; filename="pacientes.json"'
    
    return response



@login_required
def exportar_pdf(request):
    # 1. Obtenemos los datos (toda la lista de pacientes)
    # Ordenamos por especialidad para que el reporte sea lógico
    pacientes_list = Paciente.objects.all().order_by('area__nombre', 'nombre')
    
    # 2. Definimos el contexto que usará el template
    context = {
        'pacientes_list': pacientes_list
    }
    
    # 3. Llamamos a nuestra función de utilidad
    pdf = render_to_pdf('gestion/pdf_pacientes_template.html', context)
    
    # 4. Forzamos la descarga con un nombre de archivo dinámico
    if pdf:
        # Generamos un nombre de archivo con la fecha
        filename = f"reporte_pacientes_{datetime.date.today().strftime('%Y-%m-%d')}.pdf"
        
        # Creamos la respuesta
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    # Si la función render_to_pdf falló
    return HttpResponse("Error al generar el PDF.", status=500)

@login_required
def restablecer_datos(request):
    if request.method == 'POST':
        # 1. Si el usuario confirma (POST), borra los datos
        try:
            total_borrados, _ = Paciente.objects.all().delete()
            messages.success(request, f'¡Datos restablecidos! Se han borrado {total_borrados} pacientes.')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al borrar los datos: {e}')
        
        # 2. Redirige al dashboard
        return redirect('dashboard')
    
    # 3. Si es GET, solo muestra la página de confirmación
    # Contamos cuántos pacientes se van a borrar
    conteo_pacientes = Paciente.objects.count()
    context = {
        'conteo_pacientes': conteo_pacientes
    }
    return render(request, 'gestion/restablecer_confirmar.html', context)


@login_required
def editar_paciente(request, pk):
    # 1. Obtenemos el paciente específico, o mostramos un error 404 si no existe
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        # 2. Si se envía el formulario (POST), lo procesamos
        # Le pasamos 'instance=paciente' para que sepa qué paciente actualizar
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save() # Guarda los cambios en el paciente existente
            messages.success(request, '¡Paciente actualizado exitosamente!')
            return redirect('lista_pacientes') # Redirige de vuelta a la lista
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        # 3. Si es GET, mostramos el formulario con los datos del paciente
        # 'instance=paciente' llena el formulario con los datos actuales
        form = PacienteForm(instance=paciente)

    context = {
        'form': form
    }
    # Reutilizaremos un template, puedes crear uno nuevo si prefieres
    return render(request, 'gestion/editar_paciente.html', context)


def logout_view(request):
    """
    Vista personalizada para manejar el logout con un GET request.
    """
    logout(request)
    return redirect('login') # Redirige a tu página de login