# gestion/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Importamos el decorador
from .models import Paciente, Visita # MODIFICADO: Importamos Visita
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib import messages # Para mostrar mensajes de éxito
from .forms import PacienteForm, VisitaForm # MODIFICADO: Importamos VisitaForm
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from .utils import render_to_pdf # Nuestra función
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone # NUEVO: Necesario para la hora de salida


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
    # Esta vista ahora solo muestra TODOS los pacientes.
    # La búsqueda se maneja en 'buscar_paciente_dni'
    pacientes_list = Paciente.objects.all().order_by('nombre')
    
    context = {
        'pacientes': pacientes_list, # El template espera 'pacientes'
    }
    return render(request, 'gestion/lista_pacientes.html', context)

# BUSCAR PACIENTE (MODIFICADA para DNI)
@login_required
def buscar_paciente_dni(request):
    # Esta es la vista que usa el formulario de búsqueda
    dni_query = request.GET.get('dni')
    pacientes_encontrados = Paciente.objects.none() # Lista vacía por defecto

    if dni_query:
        # Buscamos pacientes que contengan el DNI
        # Usamos 'dni' porque así se llama el 'name' en el input del HTML
        pacientes_encontrados = Paciente.objects.filter(dni__icontains=dni_query)
        if not pacientes_encontrados.exists():
            messages.info(request, f'No se encontraron pacientes con el DNI: {dni_query}')
    else:
        messages.error(request, 'Por favor ingrese un DNI para buscar.')

    context = {
        'pacientes': pacientes_encontrados, # El template itera sobre 'pacientes'
        'query': dni_query
    }
    # Reutilizamos el mismo template de la lista
    return render(request, 'gestion/lista_pacientes.html', context)


# CROQUIS DEL HOSPITAL
@login_required
def croquis_hospital(request):
    # Esta vista solo renderiza el template del croquis
    return render(request, 'gestion/croquis_hospital.html')


# --- ¡FUNCIÓN MODIFICADA! ---
# VER PACIENTE (Ahora también maneja las visitas)
@login_required
def ver_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    
    # --- Lógica para registrar una NUEVA VISITA (POST) ---
    if request.method == 'POST':
        visita_form = VisitaForm(request.POST)
        if visita_form.is_valid():
            nueva_visita = visita_form.save(commit=False)
            nueva_visita.paciente = paciente
            # La hora_ingreso se pone automáticamente por el 'default' en models.py
            nueva_visita.save()
            messages.success(request, f'Visita de {nueva_visita.nombre_visitante} registrada exitosamente.')
            return redirect('ver_paciente', id=paciente.id) # Redirige a la misma página
        else:
            messages.error(request, 'Error al registrar la visita. Revisa los datos.')
            # Si hay error, el formulario inválido se pasará al contexto
    
    # --- Lógica para mostrar la página (GET) ---
    # Creamos un formulario vacío para registrar nuevas visitas
    visita_form = VisitaForm()
    
    # Obtenemos todas las visitas de este paciente, más recientes primero
    lista_visitas = Visita.objects.filter(paciente=paciente).order_by('-hora_ingreso')
    
    context = {
        'paciente': paciente,
        'visita_form': visita_form,     # El formulario para registrar
        'lista_visitas': lista_visitas, # La lista de visitas pasadas
    }
    return render(request, 'gestion/ver_paciente.html', context)


# EDITAR PACIENTE (Tu función original, ligeramente ajustada)
@login_required
def editar_paciente(request, id): # Cambié 'pk' por 'id' para consistencia
    # 1. Obtenemos el paciente específico, o mostramos un error 404 si no existe
    paciente = get_object_or_404(Paciente, id=id) # Usamos id
    
    if request.method == 'POST':
        # 2. Si se envía el formulario (POST), lo procesamos
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save() # Guarda los cambios
            messages.success(request, '¡Paciente actualizado exitosamente!')
            return redirect('lista_pacientes') # Redirige de vuelta a la lista
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        # 3. Si es GET, mostramos el formulario con los datos del paciente
        form = PacienteForm(instance=paciente)

    context = {
        'form': form,
        'paciente': paciente # Pasamos el paciente para mostrar su nombre si es necesario
    }
    # Tu template 'editar_paciente.html'
    return render(request, 'gestion/editar_paciente.html', context)


# --- ¡NUEVA FUNCIÓN! ---
# ELIMINAR PACIENTE
@login_required
def eliminar_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    try:
        # Guardamos el nombre antes de borrarlo para el mensaje
        nombre_completo = f'{paciente.nombre} {paciente.apellido}'
        paciente.delete()
        messages.success(request, f'Paciente {nombre_completo} (DNI: {paciente.dni}) ha sido eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Ocurrió un error al intentar eliminar al paciente: {e}')
    
    # Redirigimos a la lista de pacientes
    return redirect('lista_pacientes')


# --- ¡NUEVA FUNCIÓN! ---
# REGISTRAR SALIDA DE VISITA
@login_required
def registrar_salida_visita(request, visita_id):
    visita = get_object_or_404(Visita, id=visita_id)
    
    # Asegurarnos de que no se marque la salida dos veces
    if visita.hora_salida is None:
        visita.hora_salida = timezone.now()
        visita.save()
        messages.success(request, f'Salida de {visita.nombre_visitante} registrada.')
    else:
        messages.warning(request, 'Esta visita ya tenía una hora de salida registrada.')
    
    # Redirigir de vuelta a la página del paciente
    return redirect('ver_paciente', id=visita.paciente.id)


# EXPORTAR DATOS A JSON
@login_required
def exportar_json(request):
    pacientes_queryset = Paciente.objects.all().values(
        'nhc', 
        'nombre', 
        'edad', 
        'area__nombre', 
        'estado', 
        'fecha_ingreso'
    )
    pacientes_lista = list(pacientes_queryset)
    response = JsonResponse(pacientes_lista, safe=False)
    response['Content-Disposition'] = 'attachment; filename="pacientes.json"'
    return response


# EXPORTAR PDF (LISTA COMPLETA)
@login_required
def exportar_pdf(request):
    pacientes_list = Paciente.objects.all().order_by('area__nombre', 'nombre')
    context = {
        'pacientes_list': pacientes_list
    }
    pdf = render_to_pdf('gestion/pdf_pacientes_template.html', context)
    if pdf:
        filename = f"reporte_pacientes_{datetime.date.today().strftime('%Y-%m-%d')}.pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse("Error al generar el PDF.", status=500)


# --- ¡NUEVA FUNCIÓN PARA PDF INDIVIDUAL! ---
@login_required
def exportar_pdf_paciente(request, id):
    # 1. Obtenemos el paciente
    paciente = get_object_or_404(Paciente, id=id)
    # 2. Obtenemos sus visitas
    visitas = Visita.objects.filter(paciente=paciente).order_by('hora_ingreso')
    
    # 3. Definimos el contexto
    context = {
        'paciente': paciente,
        'visitas': visitas
    }
    
    # 4. Llamamos a la función de utilidad con el NUEVO MOLDE
    pdf = render_to_pdf('gestion/pdf_paciente_individual.html', context)
    
    if pdf:
        # 5. Creamos un nombre de archivo dinámico
        filename = f"ficha_paciente_{paciente.dni}_{paciente.apellido}.pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return HttpResponse("Error al generar el PDF.", status=500)


# RESTABLECER DATOS
@login_required
def restablecer_datos(request):
    if request.method == 'POST':
        try:
            total_borrados, _ = Paciente.objects.all().delete()
            messages.success(request, f'¡Datos restablecidos! Se han borrado {total_borrados} pacientes.')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al borrar los datos: {e}')
        return redirect('dashboard')
    
    conteo_pacientes = Paciente.objects.count()
    context = {
        'conteo_pacientes': conteo_pacientes
    }
    return render(request, 'gestion/restablecer_confirmar.html', context)


def logout_view(request):
    """
    Vista personalizada para manejar el logout con un GET request.
    """
    logout(request)
    return redirect('login') # Redirige a tu página de login
