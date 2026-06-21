from django.core.management.base import BaseCommand
from apps.control_morosidad.views import suspenderMorosos, generarFacturasDelMes

class Command(BaseCommand):
    # esta clase se ejecuta con el comando: python manage.py evaluar_morosidad
    help = 'Genera facturas y suspende morosos automáticamente'
    
    def handle(self, *args, **kwargs):
        # Generar facturas del mes
        self.stdout.write('Iniciando proceso automatico de morosidad...')
        # Generar facturas del mes
        facturas= generarFacturasDelMes()
        if facturas:
            self.stdout.write(self.style.SUCCESS(f'Se generaron {facturas} facturas.'))
        else:
            self.stdout.write("No se generaron facturas (no es día de cobro o no hay clientes).")
            
        # suspender morosos si ya superaron el tiempo de gracia
        desconectados= suspenderMorosos()
        self.stdout.write(self.style.SUCCESS(f'Se desconectaron {desconectados} clientes por morosidad.'))