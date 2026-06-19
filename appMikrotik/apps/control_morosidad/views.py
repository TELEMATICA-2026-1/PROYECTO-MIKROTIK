from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from django.db import models
from core.models import Cliente, Factura, Logs
from core.ApiMikrotik import suspenderCliente, reconectarCliente
from .models import ConfiguracionMorosidad
from .forms import ConfiguracionMorosidadForm, FiltroClientesMorosos
from core.autenticacion import grupo_requerido
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import calendar

def obtenerConfiguracion():
    #Funcion para obtener la configuracion de morosidad, la crea si no existe
    config, _=ConfiguracionMorosidad.objects.get_or_create(
        defaults={'diasGracia': 3, 'diaCobroMensual':1}
    )
    return config

def calcularMontoProrrateado(cliente, fechaFactura):
    """Se calcula el monto proporcional para la primera
    factura se asume meses de 30 dias (acordado en Daily)"""
    fechaRegistro = cliente.fechaRegistro
    if fechaRegistro.day == fechaFactura.day:
        return cliente.idPlan.precioUSD
    #calculamos dias desde el registro hasta el fin de mes
    diaRegistro = fechaRegistro.day
    diasRestantes = calendar.monthrange(fechaFactura.year, fechaFactura.month)[1] -(diaRegistro -1)
    
    monto = (diasRestantes/calendar.monthrange(fechaFactura.year, fechaFactura.month)[1])*cliente.idPlan.precioUSD
    return round(monto, 2)

def generarFacturaParaCliente(cliente, fechaFactura):
    """Se genera una factura para un cliente en especifico en
    la fecha indicada"""
    facturasCliente = Factura.objects.filter(idCliente=cliente).count()
    if facturasCliente == 0:
    # Si el cliente ya tiene saldo sin facturas 
        # Ahora con el calculo de prorrateado
        monto = calcularMontoProrrateado(cliente, fechaFactura)
        
    else:
        #facturas siguientes con el monto completo del plan
        monto = cliente.idPlan.precioUSD
    #actualizamos el  saldo
    factura = Factura.objects.create(
        idCliente = cliente,
        montoUSD= monto,
        fecha= fechaFactura   
    )
    cliente.saldo += monto
    cliente.save(update_fields=['saldo'])
    
    return f"Generada factura para {cliente.nombre} (Cedula {cliente.cedula}) por $ {monto}"

#generar listas de todas las facturas no montos (revisar la cantidad de caracteres) imprimir factrura con le mensaje definido en f"



def generarFacturasDelMes():
    #se generan facturas para todos los clientes el dia de cobro configurado
    config = obtenerConfiguracion()
    hoy = timezone.now().date()
    
    # si el dia de cobro es hoy
    if hoy.day != config.diaCobroMensual:
        return 0
    
    clientes = Cliente.objects.filter(borrado=False)
    totalFactura = []
    fechaFactura = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
    
    for cliente in clientes:
        if Factura.objects.filter(idCliente= cliente, fecha__date=hoy).exists():
            continue
        
        factura= generarFacturaParaCliente(cliente, fechaFactura)
        totalFactura.append(factura)
    return totalFactura


@login_required
@grupo_requerido('soporte')
def panelMorosidad(request):
    # Clientes con deuda pendiente (saldo > 0) y no borrados
    todosClientes = Cliente.objects.filter(borrado=False, saldo__gt=0)
    
    #Filtro por nombre o cedula
    filtroForm= FiltroClientesMorosos(request.POST or None)
    if filtroForm.is_valid():
        nombreCliente = filtroForm.cleaned_data.get('nombreCliente')
        if nombreCliente:
            todosClientes = todosClientes.filter(
                models.Q(nombre__icontains=nombreCliente) |
                models.Q(cedula__icontains=nombreCliente)
            )
    config = obtenerConfiguracion()
    
    if request.method == 'POST'and 'guardarConfig' in request.POST:
            form = ConfiguracionMorosidadForm(request.POST , instance=config)
            if form.is_valid():
                form.save()
                Logs.objects.create(
                    idPersonal=request.user,
                    mensaje="Configuracion de morosidad actualizada.",
                    modulo="Control Morosidad",
                    error=False
                )
                messages.success(request, "Configuracion actualizada correctamente.")
            else:
                messages.error(request, "Error en los datos del formulario. ")
                
            return redirect('panelMorosidad')
        
    else:
        form = ConfiguracionMorosidadForm(instance=config)
    
    #Paginacion de clientes morosos
    paginator = Paginator(todosClientes, 10)
    query_params = request.GET.copy()

    if 'page' in query_params:
        del query_params['page']

    clientes = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel_morosidad.html' , {
        'form': form,
        'config': config,
        'clientes': clientes,
        'query_string': query_params.urlencode(),
        'filtroForm':filtroForm,
        })


@login_required
@grupo_requerido('soporte')
def generarFacturasView(request):
    """Vista para forzar la generacion manual de facturas"""
    if request.method == 'POST':
        total = generarFacturasDelMes()
        Logs.objects.create(
            idPersonal=request.user,
            mensaje= "\n".join(str(item) for item in total) if total else "Ejecucion manual de morosidad sin cambios",
            modulo= "Control Morosidad",
            error= False
        )
        messages.success(request,f"Se generaron {len(total)} facturas para hoy. ")
        return redirect('panelMorosidad')
    return redirect('panelMorosidad')


@login_required
@grupo_requerido('soporte')
def evaluarMorosidadView(request):
    """Endpoint que puede ser llamado por cron para ejecutar la rutina automatica"""
    clientesPendientes = Cliente.objects.filter(borrado=False, saldo__gt=0, estado='Pendiente')
    clientesPagos = Cliente.objects.filter(borrado=False, saldo=0, estado='Desconectado')
    desconexiones = []
    errorDesconexiones = []
    errorReconexiones = []
    reconexiones = []
    for cliente in clientesPendientes:
        if suspenderCliente(cliente.direccionIP):
            desconexiones.append(f"Desconectando a {cliente.nombre} (Cedula {cliente.cedula}) (Direccion IP: {cliente.direccionIP}) por morosidad.")
        else:
            errorDesconexiones.append(f"Error al desconectar a {cliente.nombre} (Cedula {cliente.cedula}) (Direccion IP: {cliente.direccionIP}) por morosidad.")

        cliente.estado = 'Desconectado'
        cliente.save(update_fields=['estado'])
    for cliente in clientesPagos:
        if reconectarCliente(cliente.direccionIP):
            reconexiones.append(f"Reconectando a {cliente.nombre} (Cedula {cliente.cedula}) (Direccion IP: {cliente.direccionIP}) por pago.")
        else:
            errorReconexiones.append(f"Error al reconectar a {cliente.nombre} (Cedula {cliente.cedula}) (Direccion IP: {cliente.direccionIP}) por pago.")
        cliente.estado = 'Solvente'
        cliente.save(update_fields=['estado'])
    if desconexiones:
        Logs.objects.create(
        idPersonal=request.user,
        mensaje= "\n".join(str(item) for item in desconexiones), 
        modulo="Control Morosidad",
        error=False
        )   
    if errorDesconexiones:
        Logs.objects.create(
        idPersonal=request.user,
        mensaje= "\n".join(str(item) for item in errorDesconexiones), 
        modulo="Control Morosidad",
        error=True
        )
    if reconexiones:
        Logs.objects.create(
        idPersonal=request.user,
        mensaje= "\n".join(str(item) for item in reconexiones), 
        modulo="Control Morosidad",
        error=False
        )
    if errorReconexiones:
        Logs.objects.create(
        idPersonal=request.user,
        mensaje= "\n".join(str(item) for item in errorReconexiones), 
        modulo="Control Morosidad",
        error=True
        )
    messages.success(request, f"Proceso de evaluacion de morosidad finalizado. {len(desconexiones)} clientes desconectados, {len(reconexiones)} clientes reconectados. ")
    return redirect('panelMorosidad')
