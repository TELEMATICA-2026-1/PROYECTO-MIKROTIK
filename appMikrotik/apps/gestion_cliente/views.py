from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from core.models import Cliente, Logs
from .forms import ClienteForm, FiltroClientes
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from datetime import timedelta
from django.core.paginator import Paginator
from core.autenticacion import grupo_requerido

# Este metodo se encarga de mostrar la lista de clientes registrados, 
# con la posibilidad de aplicar filtros por nombre del cliente y cedula.
@login_required
@grupo_requerido('asistente_administrativo')
def gestion_cliente(request):
    todos_clientes = Cliente.objects.filter(borrado=False).order_by('nombre')

    if request.method == 'POST':
        filtro = FiltroClientes(request.POST)
        if filtro.is_valid():
            nombreCliente = filtro.cleaned_data.get('nombreCliente')
            estado_seleccionado = filtro.cleaned_data.get('estado')

            # Filtro por texto (Nombre O Cédula)
            if nombreCliente:
                nombreCliente = nombreCliente.strip()
                todos_clientes = todos_clientes.filter(
                    Q(nombre__icontains=nombreCliente) | 
                    Q(cedula__icontains=nombreCliente)
                )

            if estado_seleccionado:
                todos_clientes = todos_clientes.filter(estado=estado_seleccionado)
    else:
        filtro = FiltroClientes()

    paginator = Paginator(todos_clientes, 10)
    
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    page_number = request.GET.get('page')
    clientes = paginator.get_page(page_number)
        
    return render(request, 'gestion_clientes.html', {
        'clientes': clientes, 
        'filtros': filtro, 
        'query_string': query_params.urlencode() 
    })


# Este metodo se encarga de registrar un nuevo cliente, 
#si las entradas son validas, actualizamos el saldo del cliente, su estado (pendiente o exonerado) y la fecha. 
# Registra un log detallado del nuevo cliente registrado.
@login_required
@grupo_requerido('asistente_administrativo')
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            
            cliente = form.save(commit=False)
            cliente.fecha = timezone.now()

            if form.cleaned_data.get('exonerar_cliente'):
                cliente.estado = 'Exonerado'
            else:
                cliente.estado = 'Solvente'         
                cliente.borrado = False       
            
            cliente.save()   

            Logs.objects.create(
                idPersonal=request.user,
                mensaje=f"""
                Registró al nuevo cliente {cliente.nombre} (Cédula: {cliente.cedula}).
                Celular: {cliente.celular}
                Email: {cliente.email}
                Direccion: {cliente.direccion}
                Plan: {cliente.idPlan.plan} 
                Direccion Ip: {cliente.direccionIP}
                Estado: {cliente.estado}
                """,
                modulo="Gestión de Clientes",
                error=False,
                fecha=timezone.now()
            )

            return redirect('gestion_clientes') 
    else:
        form = ClienteForm() 

    return render(request, 'crear_cliente.html', {'form': form})

# Este metodo se encarga de modificar un cliente existente, 
# si las entradas son validas, actualizamos el saldo del cliente, su estado (pendiente o exonerado) y la fecha. 
# Registra un log detallado del nuevo cliente registrado.
@login_required
@grupo_requerido('asistente_administrativo')
def modificar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        cliente_viejo = Cliente.objects.get(id=id)
        form = ClienteForm(request.POST, instance=cliente)
        
        if form.is_valid():

            cliente = form.save(commit=False)

            if form.cleaned_data.get('exonerar_cliente'):
                cliente.estado = 'Exonerado'
                cliente.saldo = 0.00
            else: 
                if cliente.estado == 'Exonerado':
                    cliente.estado = 'Pendiente'
                    cliente.saldo = cliente.idPlan.precioUSD

            cliente = form.save()
            lista_cambios = []

            for campo, valor_nuevo in cliente.__dict__.items():

                if campo.startswith('_') or campo in ['id', 'borrado']:
                    continue
                
                valor_viejo = getattr(cliente_viejo, campo)
                
                if valor_nuevo != valor_viejo:
                    lista_cambios.append(f"{campo}: {valor_viejo} => {valor_nuevo}")

            if lista_cambios:
                mensaje_log = f"Modificó al cliente {cliente.nombre} (ID: {cliente.id}). Cambios realizados:\n\n" + "\n".join(lista_cambios)
            else:
                mensaje_log = f"El operador guardó al cliente {cliente.nombre} (ID: {cliente.id}) sin realizar cambios."

            Logs.objects.create(
                idPersonal=request.user,
                mensaje=mensaje_log,
                modulo="Gestión de Clientes",
                error=False,
                fecha=timezone.now()
            )

            return redirect('gestion_clientes')
            
    else:
        form = ClienteForm(instance=cliente)
        
    return render(request, 'modificar_cliente.html', {'form': form, 'cliente': cliente})

# Este metodo se encarga de borrar un cliente existente, 
# si las entradas son validas, actualizamos su estado de borrado logico y lo cambiamos a TRUE, esto pondra al cliente como eliminado. 
# Registra un log detallado del nuevo cliente registrado.
@login_required
@grupo_requerido('asistente_administrativo')
def borrar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        
        cliente.borrado = True

        cliente.save()

        Logs.objects.create(
                idPersonal=request.user,
                mensaje=f"""
                Se Elimino al cliente {cliente.nombre} (Cédula: {cliente.cedula}).
                Celular: {cliente.celular}
                Email: {cliente.email}
                Direccion: {cliente.direccion}
                Plan: {cliente.idPlan.plan} 
                Direccion Ip:{cliente.direccionIP}
                Estado: {cliente.estado}
                """,
                modulo="Gestión de Clientes",
                error=False,
                fecha=timezone.now()
            )
        
        return redirect('gestion_clientes', 0)
    return render(request, 'confirmar_borrar.html', {'cliente': cliente})

def api_tarjetas_dashboard(request):
    
    solventes = Cliente.objects.filter(estado='Solvente', borrado=False).count()
    exonerados = Cliente.objects.filter(estado='Exonerado', borrado=False).count()
    pendientes = Cliente.objects.filter(estado='Pendiente', borrado=False).count()
    desconectados = Cliente.objects.filter(estado='Desconectado', borrado=False).count()
    
    data = {
        'solventes': solventes,
        'exonerados': exonerados,
        'pendientes': pendientes,
        'desconectados': desconectados,
    }
    
    return JsonResponse(data)

def api_graficos_dashboard(request):
    hace_7_dias = timezone.now() - timedelta(days=7)
    
    logs_query = (
        Logs.objects.filter(fecha__gte=hace_7_dias)
        .annotate(dia=TruncDay('fecha'))
        .values('dia')
        .annotate(
            exitos=Count('id', filter=Q(error=False)),
            errores=Count('id', filter=Q(error=True))
        )
        .order_by('dia')
    )
    
    labels_logs = []
    series_exitos = []
    series_errores = []
    
    dias_es = {
        'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mie', 
        'Thu': 'Jue', 'Fri': 'Vie', 'Sat': 'Sab', 'Sun': 'Dom'
    }
    
    for log in logs_query:
        dia_en = log['dia'].strftime('%a')
        labels_logs.append(dias_es.get(dia_en, dia_en))
        series_exitos.append(log['exitos'])
        series_errores.append(log['errores'])

    cobranzas_query = (
             Cliente.objects.filter(borrado=False, estado__in=['Solvente', 'Pendiente'])
             .values('estado')
            .annotate(total=Count('id'))
    )
    
    distribucion_cobranzas = {item['estado']: item['total'] for item in cobranzas_query}
    json_final = {
        'historico_logs': {
            'labels': labels_logs,
            'exitos': series_exitos,
            'errores': series_errores
        },
        'estado_cobranzas': distribucion_cobranzas
    }

    return JsonResponse(json_final, json_dumps_params={'ensure_ascii': False})

# Este metodo se encarga de mostrar la informacion detallada de un cliente especifico,
# cargando tanto sus datos personales como los del servicio contratado de forma de solo lectura.
@login_required
@grupo_requerido('asistente_administrativo')
def detalles_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    return render(request, 'detalles_cliente.html', {'cliente': cliente})
