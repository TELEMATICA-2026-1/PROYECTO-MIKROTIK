from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from core.models import Cliente, Factura, Logs
from core.ApiMikrotik import suspenderCliente, reconectarCliente
from .models import ConfiguracionMorosidad, SeguimientoMorosidad
from .forms import ConfiguracionMorosidadForm
from core.autenticacion import grupo_requerido

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
    if fechaRegistro.date() == fechaFactura.date():
        return cliente.idPlan.precioUSD
    #calculamos dias desde el registro hasta el fin de mes
    diaRegistro = fechaRegistro.day
    diasRestantes =30 -(diaRegistro -1)
    if diasRestantes <= 0:
        diasRestantes = 30
    monto = (diasRestantes/30)*cliente.idPlan.precioUSD
    return round(monto, 2)

def generarFacturaParaCliente(cliente, fechaFactura):
    """Se genera una factura para un cliente en especifico en
    la fecha indicada"""
    seguimiento, _= SeguimientoMorosidad.objects.get_or_create(cliente=cliente)
    esPrimera = not seguimiento.primeraFacturaGenerada
    
    if esPrimera:
    # Si el cliente ya tiene saldo sin facturas 
        if cliente.saldo > 0 and not Factura.objects.filter(idCliente=cliente).exists():
            # No se generan facturas dobles
            seguimiento.primeraFacturaGenerada = True
            seguimiento.save()
            return None
        # Ahora con el calculo de prorrateado
        monto = calcularMontoProrrateado(cliente, fechaFactura)
        seguimiento.primeraFacturaGenerada=True
        seguimiento.save()
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
    
    #Se registra en Logs
    Logs.objects.create(
        idPersonal=1,
        modulo= "Control Morosidad",
        mensaje = f"Generada factura para {cliente.nombre} (Cedula {cliente.cedula}) por $ {monto}",
        error= False
    )
    return factura

def actualizarEstadoCliente(cliente):
    # sourcery skip: merge-else-if-into-elif, remove-pass-elif
    #Esta funcion revisa el saldo del cliente y actualiza su estado
    estadoAnterior = cliente.estado
    
    #Si el cliente tiene el estado de exonerado no se realizan cambios
    if estadoAnterior == 'Exonerado':
        return False
    seguimiento, _= SeguimientoMorosidad.objects.get_or_create(cliente=cliente)
    config = obtenerConfiguracion()
    nuevoEstado = estadoAnterior
    
    if  cliente.saldo <=0:
        # Cliente solvente
        nuevoEstado = 'Solvente'
        if seguimiento.fechaInicioPendiente:
            seguimiento.fechaInicioPendiente = None
            seguimiento.save()
    else:
        # si tiene deuda evaluamos el estado actual
        if estadoAnterior == 'Solvente':
            nuevoEstado = 'Pendiente'
            seguimiento.fechaInicioPendiente = timezone.now()
            seguimiento.save()
        elif estadoAnterior == 'Pendiente':
            # si ya estaba pendiente se verifican los dias de gracia
            if seguimiento.fechaInicioPendiente:
                diasEnPendiente = (timezone.now()- seguimiento.fechaInicioPendiente).days
                if diasEnPendiente >= config.diasGracia:
                    nuevoEstado = 'Desconectado'
                    
            else:
                seguimiento.fechaInicioPendiente = timezone.now()
                seguimiento.save()
        elif estadoAnterior == 'Desconectado':
            #Caso de que siga con deuda, se mantiene con estado desconectado
            pass
    
    #Si hubo cambio de estado
    if nuevoEstado != estadoAnterior:
        cliente.estado = nuevoEstado
        cliente.save(update_fields=['estado'])
        
        #Se ejecutan los metodos del router Mikrotik
        try:
            if nuevoEstado == 'Desconectado':
                suspenderCliente(cliente.direccionIP)
            elif nuevoEstado == 'Solvente':
                reconectarCliente(cliente.direccionIP)
        except Exception as e:
            Logs.objects.create(
                idPersonal=1,
                modulo="Control Morosidad",
                mensaje=f"Error al {'suspender' if nuevoEstado=='Desconectado' else 'reactivar'} cliente {cliente.nombre} (IP {cliente.direccionIP}): {str(e)}",
                error=True
            )
        
        # Registramos los Logs del cambio de estado
        Logs.objects.create(
            idPersonal=1,
            modulo="Control Morosidad",
            mensaje=f"Cambio automatico de estado: {cliente.nombre} (Cedula {cliente.cedula}) de '{estadoAnterior}' a '{nuevoEstado}'. Saldo actual: {cliente.saldo}$",
            error=False
        )
        return True
    return False


def procesarMorosidadMasiva():
    # sourcery skip: inline-immediately-returned-variable, sum-comprehension
    # Se evalua y actuaiza el estado de todos los clientes activos
    clientes = Cliente.objects.filter(borrado=False)
    cambios = 0
    for cliente in clientes:
        if actualizarEstadoCliente(cliente):
            cambios += 1
    return cambios

def generarFacturasDelMes():
    #se generan facturas para todos los clientes el dia de cobro configurado
    config = obtenerConfiguracion()
    hoy = timezone.now().date()
    
    # si el dia de cobro es hoy
    if hoy.day != config.diaCobroMensual:
        return 0
    
    clientes = Cliente.objects.filter(borrado=False)
    contador = 0
    fechaFactura = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
    
    for cliente in clientes:
        if Factura.objects.filter(idCliente= cliente, fecha__date=hoy).exists():
            continue
        
        generarFacturaParaCliente(cliente, fechaFactura)
        contador +=1
        
        actualizarEstadoCliente(cliente)
    return contador

@login_required
@grupo_requerido('asistente_administrativo')
def panelMorosidad(request):
    """Vista principal del panel de morosidad: muestra configuracion y permite ejecutar evaluacion manual"""
    config = obtenerConfiguracion()
    
    if request.method == 'POST':
        if 'ejecutarAhora' in request.POST:
            cambios = procesarMorosidadMasiva()
            messages.success(request, f"Evaluacion manual ejecutada. {cambios} clientes cambiaron de estado.")
            return redirect('panelMorosidad')
        elif 'guardarConfig' in request.POST:
            form = ConfiguracionMorosidadForm(request.POST , instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, "Configuracion actualizada correctamente.")
            else:
                messages.error(request, "Error en los datos del formulario. ")
            return redirect('panelMorosidad')
    else:
        form = ConfiguracionMorosidadForm(instance=config)
        
    return render(request, 'panel_morosidad.html' , {'form': form, 'config': config})


@login_required
@grupo_requerido('asistente_administrativo')
def generarFacturasView(request):
    """Vista para forzar la generacion manual de facturas"""
    if request.method == 'POST':
        total = generarFacturasDelMes()
        messages.success(request,f"Se generaron {total} facturas para hoy. ")
        return redirect('panelMorosidad')
    return redirect('panelMorosidad')


@login_required
@grupo_requerido('asistente_administrativo')
def evaluarMorosidadView(request):
    """Endpoint que puede ser llamado por cron para ejecutar la rutina automatica"""
    if request.method == 'GET':
        cambios = procesarMorosidadMasiva()
        facturas = generarFacturasDelMes()
        return render(request, 'resultado_ejecucion.html', {
            'cambios': cambios,
            'facturas': facturas
        })
    return redirect('panelMorosidad')





        
            

