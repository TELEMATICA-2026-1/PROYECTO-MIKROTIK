from django.db import models
from core.models import Cliente

class ConfiguracionMorosidad(models.Model):
    """Configuracion global del modulo de morosidad, con 3 dias de gracia
    y que la factura se genere el primer dia del mes"""
    
    diasGracia= models.PositiveSmallIntegerField(default=3)
    diaCobroMensual= models.PositiveSmallIntegerField(default=1)
    
    
    def __str__(self):
        return f"Dias de gracia: {self.diasGracia} - Dia de cobro: {self.diaCobroMensual}"    

    