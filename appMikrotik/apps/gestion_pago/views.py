from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from core.models import Pago, Logs, Cliente
from .forms import PagoForm, FiltroPagos, FiltroPendientes
from django.contrib.auth.decorators import login_required
from core.autenticacion import grupo_requerido


# Create your views here.

# Este metodo se encarga de mostrar la lista de pagos registrados, 
# con la posibilidad de aplicar filtros por nombre del cliente y rango de fechas.
@login_required
@grupo_requerido('asistente_administrativo')
def gestion_pago(request,id):

    if id != 0:
        todos_pagos = Pago.objects.filter(idCliente__id=id).order_by('-fecha')
    else:
        todos_pagos = Pago.objects.all().order_by('-fecha')

    if request.method == 'POST':
        filtro = FiltroPagos(request.POST)
        if filtro.is_valid():
            nombreCliente = filtro.cleaned_data.get('nombreCliente')
            fecha_inicio = filtro.cleaned_data.get('fecha_inicio')
            fecha_fin = filtro.cleaned_data.get('fecha_fin')

            if nombreCliente:
                todos_pagos = todos_pagos.filter(Q(idCliente__nombre__icontains=nombreCliente) | Q(idCliente__cedula__icontains=nombreCliente))

            if fecha_inicio and fecha_fin:
                todos_pagos = todos_pagos.filter(fecha__range=(fecha_inicio, fecha_fin))
            elif fecha_inicio:
                todos_pagos = todos_pagos.filter(fecha__gte=fecha_inicio)
            elif fecha_fin:
                todos_pagos = todos_pagos.filter(fecha__lte=fecha_fin)

            todos_pagos = todos_pagos.order_by('-fecha')
    else:
        filtro = FiltroPagos()

    paginator = Paginator(todos_pagos, 10)
    query_params = request.GET.copy()

    if 'page' in query_params:
        del query_params['page']
    
    pagos = paginator.get_page(request.GET.get('page'))
        
    return render(request, 'gestion_pagos.html', {'pagos': pagos, 'filtros': filtro, 'query_string': query_params.urlencode()})


# Este metodo se encarga de registrar un nuevo pago para un cliente específico, 
# actualizando el saldo del cliente y su estado si es necesario y si las entradas son validas. 
# Registra un log detallado del nuevo pago registrado, incluyendo el monto y la tasa aplicada.
@login_required
@grupo_requerido('asistente_administrativo')
def crear_pago(request,id):
    cliente = get_object_or_404(Cliente,borrado=False, id=id)

    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)

        if form.is_valid():
            montoUSD = form.cleaned_data.get('montoUSD')
            fecha = form.cleaned_data.get('fecha')
            cliente.fecha = fecha
            cliente.saldo -= montoUSD

            if cliente.saldo < 0:
                cliente.saldo += montoUSD
                return render(request, 'crear_pago.html', {
                    'form': form, 
                    'cliente': cliente,
                    'fecha': timezone.now(),
                    'error': 'El monto del pago excede el saldo pendiente del cliente.'
                    })
            elif cliente.saldo == 0:
                cliente.estado = 'Solvente'

            nuevo_pago = form.save(commit=False)
            nuevo_pago.idPersonal = request.user
            nuevo_pago.idCliente = cliente
            nuevo_pago.save()

            cliente.save()

            Logs.objects.create(
                idPersonal=request.user,
                mensaje=f"""Registró un nuevo pago para el cliente {cliente.nombre} (Cédula: {cliente.cedula}). 
Monto: {montoUSD}$
Tasa: {nuevo_pago.tasa}""",
                modulo = "Gestion de pagos",
                error = False,
                fecha = timezone.now()
            )

            return redirect('gestion_pagos')
    else:
        form = PagoForm()
    
    print(form)
    return render(request, 'crear_pago.html', {'form': form, 'cliente': cliente, 'fecha': timezone.now()})


# Este metodo se encarga de modificar un pago existente, 
# actualizando el saldo del cliente y su estado si es necesario y si las entradas son validas, 
# y registrando un log detallado de los cambios realizados.
@login_required
@grupo_requerido('asistente_administrativo')
def modificar_pago(request, id):
    pago = get_object_or_404(Pago, id=id)
    cliente = pago.idCliente
    pago_anterior = Pago.objects.get(id=id)
    montoAnterior = pago.montoUSD

    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES, instance=pago)
        
        if form.is_valid():
            cliente = pago.idCliente
            montoNuevo = form.cleaned_data.get('montoUSD')            
            diferencia = montoNuevo - montoAnterior
            cliente.saldo -= diferencia
                
            if cliente.saldo < 0:
                return render(request, 'modificar_pago.html', {
                    'form': form, 
                    'cliente': cliente, 
                    'fecha': pago.fecha,
                    'error': 'El monto del pago excede el saldo pendiente del cliente.'
                })
            elif cliente.saldo == 0:
                cliente.estado = 'Solvente'
            else:
                cliente.estado = 'Pendiente'

            cliente.save()

            pago = form.save(commit=False)
            pago.idPersonal = request.user

            lista_cambios = []

            for campo, valor_nuevo in pago.__dict__.items():

                if campo.startswith('_') or campo in ['id', 'borrado']:
                    continue
                
                valor_viejo = getattr(pago_anterior, campo)
                
                if valor_nuevo != valor_viejo:
                    lista_cambios.append(f"{campo}: {valor_viejo} => {valor_nuevo}")

            if lista_cambios:
                mensaje_log = f"Modificó al pago (ID: {pago.id}). Cambios realizados:\n\n" + "\n".join(lista_cambios)
            else:
                mensaje_log = f"El operador guardó al pago (ID: {pago.id}) sin realizar cambios."
            
            pago.save(update_fields=['montoUSD', 'tasa', 'comprobante', 'metodo'])
            form.save_m2m()
            
            Logs.objects.create(
                idPersonal=request.user, 
                mensaje=mensaje_log,
                modulo = "Gestion de pagos",
                error = False,
                fecha = timezone.now()
            )
            
            return redirect('gestion_pagos')
    else:
        form = PagoForm(instance=pago)
        
    return render(request, 'modificar_pago.html', {'form': form, 'cliente': cliente, 'fecha': pago.fecha})


# Este metodo se encarga de mostrar los detalles de un pago específico, 
# incluyendo la información del cliente asociado.
@login_required
@grupo_requerido('asistente_administrativo')
def mostrar_detalles(request, id):
    pago = get_object_or_404(Pago, id=id)
    cliente = pago.idCliente
    return render(request, 'detalles_pago.html', {'pago': pago, 'cliente': cliente})


# Este metodo se encarga de mostrar la lista de clientes con pagos pendientes,
# con la posibilidad de aplicar un filtro por nombre del cliente o cedula. 
@login_required
@grupo_requerido('asistente_administrativo')
def pendientes(request):
    clientes_pendientes = Cliente.objects.filter(borrado=False,saldo__gt=0).order_by('nombre')
    filtro = FiltroPendientes()

    if request.method == 'POST':
        filtro = FiltroPendientes(request.POST)
        if filtro.is_valid():
            nombreCliente = filtro.cleaned_data.get('nombreCliente')

            if nombreCliente:
                clientes_pendientes = clientes_pendientes.filter(Q(nombre__icontains=nombreCliente) | Q(cedula__icontains=nombreCliente)).order_by('nombre')

    paginator = Paginator(clientes_pendientes, 10)
    query_params = request.GET.copy()

    if 'page' in query_params:
        del query_params['page']

    clientes = paginator.get_page(request.GET.get('page'))

    return render(request, 'pendientes.html', {'clientes': clientes, 'filtros': filtro, 'query_string': query_params.urlencode()})
