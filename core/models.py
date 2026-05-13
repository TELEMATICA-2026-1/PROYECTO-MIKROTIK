from django.db import models

# Los modelos de la aplicación solamente enbarcan las entidades plantillas
# es decir, no contienen datos, sino que definen la estructura q tiene la BD
# cada modelo es una clase que representa una tabla en la base de datos. 
# cada atributo de la clase representa un campo en la tabla

class Operacion(models.Model):

    id_operacion = models.AutoField(primary_key=True)
    numero1 = models.FloatField()
    numero2 = models.FloatField()
    operacion = models.CharField(max_length=20)
    resultado = models.FloatField()

    class Meta:
        db_table = 'operacion'
        verbose_name = 'Operacion'
        verbose_name_plural = 'Operaciones'
    
    def __str__(self):
        return f"{self.numero1} {self.operacion} {self.numero2} = {self.resultado}"
