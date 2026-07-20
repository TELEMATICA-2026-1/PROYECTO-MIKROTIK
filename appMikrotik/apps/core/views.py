from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from .forms import LoginForm, FiltroLogs
from django.contrib.auth.decorators import login_required
from core.models import Logs


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
                                           'error':'Usuario o contraseña incorrectos.'})
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
