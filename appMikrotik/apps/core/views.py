from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from .forms import LoginForm, FiltroLogs
from django.contrib.auth.decorators import login_required
from core.models import Logs
import os
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa
import datetime

# Este metodo se encarga de mostrar la página de inicio del sistema.
@login_required
def home(request):
    return render(request, 'home.html')

# Este metodo se encarga de cerrar la sesión del usuario actual y redirigirlo a la página de inicio de sesión.
@login_required
def signout(request):
    logout(request)
    return redirect('login')

# Este metodo se encarga de manejar el proceso de inicio de sesión, 
# autenticando al usuario y redirigiéndolo a la página de inicio si las credenciales son válidas, 
# o mostrando un mensaje de error si el formulario no es válido.
def signin(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'form':form, 
                                           'error':'La contraseña o el nombre de usuario son incorrectos'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Este metodo se encarga de mostrar los logs del sistema, 
# con la posibilidad de aplicar un filtro por rango de fechas.
@login_required
def logs(request):
    todos_logs = Logs.objects.all().order_by('-fecha')
    if request.method == 'POST':
        form = FiltroLogs(request.POST)
        if form.is_valid():
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')

            if fecha_inicio and fecha_fin:
                todos_logs = todos_logs.filter(fecha__range=(fecha_inicio, fecha_fin))
            elif fecha_inicio:
                todos_logs = todos_logs.filter(fecha__gte=fecha_inicio)
            elif fecha_fin:
                todos_logs = todos_logs.filter(fecha__lte=fecha_fin)
    else:
        form = FiltroLogs()

    paginator = Paginator(todos_logs, 10)
    query_params = request.GET.copy()

    if 'page' in query_params:
        del query_params['page']

    logs = paginator.get_page(request.GET.get('page'))

    return render(request, 'logs.html', {'logs': logs, 
                                         'filtros': form,
                                         'query_string': query_params.urlencode()})

@login_required
def exportar_logs_pdf(request):
    todos_logs = Logs.objects.all().order_by('-fecha')
    
    # 1. Capturar los parámetros GET que vienen desde el botón del HTML
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # 2. Aplicar filtros si existen en la URL
    if fecha_inicio and fecha_fin:
        todos_logs = todos_logs.filter(fecha__range=(fecha_inicio, fecha_fin))
    elif fecha_inicio:
        todos_logs = todos_logs.filter(fecha__gte=fecha_inicio)
    elif fecha_fin:
        todos_logs = todos_logs.filter(fecha__lte=fecha_fin)

    # 3. Construcción dinámica y exacta de la ruta del logo MikroCore
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    raiz_app = os.path.abspath(os.path.join(dir_actual, '..', '..'))
    ruta_logo = os.path.join(raiz_app, 'static', 'images', 'Logo-1.png')

    # Formatear las fechas de los filtros antes del contexto
    fecha_inicio_formateada = None
    fecha_fin_formateada = None

    if fecha_inicio:
        try:
            fecha_inicio_formateada = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            fecha_inicio_formateada = fecha_inicio

    if fecha_fin:
        try:
            fecha_fin_formateada = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            fecha_fin_formateada = fecha_fin

    # 4. Pasar los datos recopilados al contexto de la plantilla del PDF
    context = {
        'logs': todos_logs,
        'ruta_logo': ruta_logo,
        'fecha_reporte': datetime.datetime.now().strftime("%d/%m/%Y a las %I:%M:%S %p").replace("AM", "a.m.").replace("PM", "p.m."),
        'fecha_inicio': fecha_inicio_formateada,
        'fecha_fin': fecha_fin_formateada,
    }

    # 5. Cargar la plantilla directamente desde la raíz de templates
    template = get_template('reporte_logs_pdf.html')
    html = template.render(context)
    
    # 6. Crear la respuesta binaria de tipo PDF para el navegador
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_logs_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    # xhtml2pdf se encarga de transformar el HTML en el documento final
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al estructurar el reporte PDF', status=500)
    return response