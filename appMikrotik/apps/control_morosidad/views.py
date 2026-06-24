from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from django.db import models
from core.models import Cliente, Factura, Logs
from core.ApiMikrotik import suspenderCliente, reconectarCliente
from .models import ConfiguracionMorosidad
from .forms import ConfiguracionMorosidadForm, FiltroClientesMorosos
from core.autenticacion import grupo_requerido
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import calendar


# Usuario del sistema para logs automatizados
system_user = User.objects.get(username='Sistema')

def obtenerConfiguracion():
    #Funcion para obtener la configuracion de morosidad, la crea si no existe
    config, _=ConfiguracionMorosidad.objects.get_or_create(
        defaults={'diasGracia': 3, 'diaCobroMensual':1}
    )
    return config

def calcularMontoProrrateado(cliente, fechaFactura):
    #Se calcula el monto proporcional para la primera factura
    fechaRegistro = cliente.fechaRegistro.date()
    if fechaRegistro == fechaFactura.date():
        return cliente.idPlan.precioUSD
    #calculamos dias desde el registro hasta el fin de mes
    diaRegistro = fechaRegistro.day
    diasRestantes = calendar.monthrange(fechaRegistro.year, fechaRegistro.month)[1] -(diaRegistro -1)
    
    monto = (Decimal((diasRestantes))/Decimal((calendar.monthrange(fechaRegistro.year, fechaRegistro.month)[1])))*cliente.idPlan.precioUSD
    return monto.quantize(Decimal('0.01'))  # Redondear a 2 decimales

def generarFacturaParaCliente(cliente, fechaFactura):
    #Se genera una factura para un cliente en especifico en la fecha indicada"""
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
    
    # si el dia de cobro es hoy, retorna lista vacia
    if hoy.day != config.diaCobroMensual:
        return []
    
    clientes = Cliente.objects.filter(borrado=False)
    totalFactura = []
    fechaFactura = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
    
    for cliente in clientes:
        # evita duplicar facturas si ya existe una factura 
        if Factura.objects.filter(idCliente= cliente, fecha__date=hoy).exists():
            continue
        
        factura= generarFacturaParaCliente(cliente, fechaFactura)
        
        if factura:
            totalFactura.append(factura)
    return totalFactura


def suspenderMorosos():
    #suspende a toods los clientes que ya superarron los dias de gracia
    clientesPendientes = Cliente.objects.filter(
        borrado=False,
        saldo__gt=0, 
        estado='Pendiente', 
        )
    
    desconexiones = []
    errores = []
    for cliente in clientesPendientes:
        if suspenderCliente(cliente.direccionIP):
            cliente.estado = 'Desconectado'
            cliente.save(update_fields=['estado'])
            desconexiones.append(f"Desconectando a {cliente.nombre} (Cedula {cliente.cedula}) (Direccion IP: {cliente.direccionIP}) por morosidad.")
        else:
            # No cambia el estado, solo se registra el error
            errores.append(f"Error al desconectar a {cliente.nombre} (Cedula {cliente.cedula}) (Direccion IP: {cliente.direccionIP}) por morosidad.")
        
    
    if desconexiones:
        Logs.objects.create(
        idPersonal=system_user,
        mensaje= "\n".join(desconexiones), 
        modulo="Control Morosidad",
        error=False
        )
    if errores:
        Logs.objects.create(
        idPersonal=system_user,
        mensaje= "\n".join(errores), 
        modulo="Control Morosidad",
        error=True
        )
    
    return len(desconexiones)

def reconectarClienteEspecifico(cliente):
    #Reconecta a un cliente especifico que ya pago su deuda
    if reconectarCliente(cliente.direccionIP):
        Logs.objects.create(
            idPersonal=system_user,
            mensaje=f"Reconectando a {cliente.nombre} (Cedula {cliente.cedula}) (Direccion IP: {cliente.direccionIP}) por pago.",
            modulo="Control Morosidad",
            error=False
        )
        return True
    else:
        Logs.objects.create(
            idPersonal=system_user,
            mensaje=f"Error al reconectar a {cliente.nombre} (Cedula {cliente.cedula}) (Direccion IP: {cliente.direccionIP}) por pago.",
            modulo="Control Morosidad",
            error=True
        )
        return False

# Vistas manuales para el panel de control de morosidad
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
    #Vista para forzar la generacion manual de facturas
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
    #Vista manual que ejecuta suspension de morosos y reconexion de clientes que pagaron
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
        mensaje= "\n".join(desconexiones), 
        modulo="Control Morosidad",
        error=False
        )   
    if errorDesconexiones:
        Logs.objects.create(
        idPersonal=request.user,
        mensaje= "\n".join(errorDesconexiones), 
        modulo="Control Morosidad",
        error=True
        )
    if reconexiones:
        Logs.objects.create(
        idPersonal=request.user,
        mensaje= "\n".join(reconexiones), 
        modulo="Control Morosidad",
        error=False
        )
    if errorReconexiones:
        Logs.objects.create(
        idPersonal=request.user,
        mensaje= "\n".join(errorReconexiones), 
        modulo="Control Morosidad",
        error=True
        )
    messages.success(request, f"Proceso de evaluacion de morosidad finalizado. {len(desconexiones)} clientes desconectados, {len(reconexiones)} clientes reconectados. ")
    return redirect('panelMorosidad')
