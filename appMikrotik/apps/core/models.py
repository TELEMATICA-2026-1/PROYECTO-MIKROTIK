from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from pyBCV import Currency

# Funcion para obtener la tasa de cambio actual
def obtener_tasa_actual():
        try:
            tasa = Currency().get_rate('USD',prettify=False)
            return round(float(tasa), 2)
        except Exception as e:
            print(f"Error al obtener la tasa de cambio: {e}")
            return None

# Este archivo define los modelos de datos para la aplicación core, 
# incluyendo los modelos para planes de internet, clientes, facturas, pagos y logs del sistema.
class Plan(models.Model):
    plan = models.CharField(max_length=20)
    precioUSD = models.DecimalField(max_digits=10, decimal_places=2)
    velocidad_subida = models.DecimalField(max_digits=10, decimal_places=2)
    velocidad_bajada = models.DecimalField(max_digits=10, decimal_places=2)
    borrado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.plan}"
    
class Cliente(models.Model):
    class SeleccionEstado(models.TextChoices):
        SOLVENTE = 'Solvente', 'Solvente'
        EXONERADO = 'Exonerado', 'Exonerado'
        PENDIENTE = 'Pendiente', 'Pendiente'
        DESCONECTADO = 'Desconectado', 'Desconectado'  

    idPlan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    cedula = models.CharField(max_length=9)
    celular = models.CharField(max_length=12)
    direccion = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    direccionIP = models.GenericIPAddressField(protocol='IPv4')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=SeleccionEstado.choices)
    fechaRegistro = models.DateTimeField(default=timezone.now)
    borrado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cedula} | {self.nombre} | {self.celular} | {self.email} | {self.saldo}$ | {self.estado}"
    
class Factura(models.Model):
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    montoUSD = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.idCliente.cedula} | {self.idCliente.nombre} | {self.montoUSD}$ | {self.fecha}"

class Pago(models.Model):
    class SeleccionMetodo(models.TextChoices):
        TRANSFERENCIA = 'Transferencia', 'Transferencia'
        PAGO_MOVIL = 'Pago Móvil', 'Pago Móvil'
        ZELLE = 'Zelle', 'Zelle'
        EFECTIVOBS = 'Efectivo Bs', 'Efectivo Bs'
        EFECTIVODOLARES = 'Efectivo $', 'Efectivo $'

    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    idPersonal = models.ForeignKey(User, on_delete=models.CASCADE)
    montoUSD = models.DecimalField(max_digits=10, decimal_places=2)
    tasa = models.DecimalField(max_digits=10, decimal_places=2, default=obtener_tasa_actual)
    metodo = models.CharField(max_length=20, choices=SeleccionMetodo.choices)
    fecha = models.DateTimeField(default=timezone.now)
    comprobante = models.ImageField(upload_to='comprobantes/%Y/%m/%d/', null=True, blank=True)

    def __str__(self):
        return f"{self.idCliente.cedula} {self.idCliente.nombre} | {self.idPersonal.username} | {self.montoUSD}$ | {self.fecha}"
    
    @property
    def monto_bs(self):
        return round(self.montoUSD * self.tasa,2)
    
class Logs(models.Model):
    idPersonal = models.ForeignKey(User, on_delete=models.CASCADE)
    modulo = models.CharField(max_length=30)
    mensaje = models.TextField()
    error = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.idPersonal.username} | {self.modulo} | {self.fecha}"