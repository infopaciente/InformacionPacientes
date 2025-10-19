# gestion/utils.py
import io
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    """
    Función para renderizar un template de Django a un PDF.
    """
    # 1. Carga el template
    template = get_template(template_src)
    
    # 2. Renderiza el HTML con el contexto
    html = template.render(context_dict)
    
    # 3. Crea un buffer de memoria para el PDF
    result = io.BytesIO()
    
    # 4. Genera el PDF
    # encoding='UTF-8' es clave para manejar tildes y ñ
    pdf = pisa.pisaDocument(
        io.BytesIO(html.encode("UTF-8")), 
        result,
        encoding='UTF-8'
    )
    
    # 5. Si no hubo errores, devuelve el PDF
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    # Si hubo un error
    return HttpResponse("Error al generar el PDF: %s" % pdf.err, status=400)