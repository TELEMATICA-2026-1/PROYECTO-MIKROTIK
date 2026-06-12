from django.db import models
from core.models import Cliente

class ConfiguracionMorosidad(models.Model):
    """Configuracion global del modulo de morosidad, con 3 dias de gracia
    y que la factura se genere el primer dia del mes"""
    
    diasGracia= models.PositiveSmallIntegerField(default=3)
    diaCobroMensual= models.PositiveSmallIntegerField(default=1)
    
    
    def __str__(self):
        return f"Dias de gracia: {self.diasGracia} - Dia de cobro: {self.diaCobroMensual}"    

class SeguimientoMorosidad(models.Model):
    #Se registra cuando un cliente entro en estado Pendiente y su ultima facturacion
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='seguimientoMorosidad')
    fechaInicioPendiente = models.DateTimeField(null=True, blank=True)
    fechaUltimaEvaluacion = models.DateTimeField(auto_now=True)
    primeraFacturaGenerada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente.nombre} - Pendiente desde: {self.fechaInicioPendiente}"

# Para Reevaluar cliente automaticamente cuando se registra un pago

from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Pago

@receiver(post_save, sender=Pago)
def reevaluarClientePorPago(sender, instance, created, **kwargs):
    """Cada vez que se guarda un pago, reevalua el estado del cliente asociado"""
    from .views import actualizarEstadoCliente
    cliente = instance.idCliente
    actualizarEstadoCliente(cliente)
    