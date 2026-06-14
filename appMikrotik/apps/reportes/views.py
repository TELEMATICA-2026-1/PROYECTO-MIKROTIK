from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from django.contrib.auth.decorators import login_required

# Importamos los modelos de la app core
from core.models import Pago, Cliente, Logs

# 1. Vista de la interfaz HTML (Carga el cascarón de la página rápido)
@login_required
def gestion_reportes(request):
    return render(request, 'gestion_reportes.html')

def api_datos_reportes(request):
    # Ingresos por Método de Pago
    g1_consultas = Pago.objects.values('metodo').annotate(total_ingresos=Sum('montoUSD'))
    g1_labels = [item['metodo'] for item in g1_consultas]
    g1_data = [float(item['total_ingresos']) for item in g1_consultas]

    # Clientes por Estado
    g2_consultas = Cliente.objects.filter(borrado=False).values('estado').annotate(total_clientes=Count('id'))
    g2_labels = [item['estado'] for item in g2_consultas]
    g2_data = [item['total_clientes'] for item in g2_consultas]

    # Planes más Vendidos
    g3_consultas = Cliente.objects.filter(borrado=False).values('idPlan__plan').annotate(total_clientes=Count('id'))
    g3_labels = [item['idPlan__plan'] for item in g3_consultas]
    g3_data = [item['total_clientes'] for item in g3_consultas]

    # Historial de Ingresos Mensuales
    g4_consultas = Pago.objects.annotate(mes_num=ExtractMonth('fecha')).values('mes_num').annotate(total_mes=Sum('montoUSD')).order_by('mes_num')
    meses_espanol = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    g4_labels = [meses_espanol.get(item['mes_num'], f"Mes {item['mes_num']}") for item in g4_consultas if item['mes_num'] is not None]
    g4_data = [float(item['total_mes']) for item in g4_consultas if item['mes_num'] is not None]

    # Métricas de Logs (Errores por módulo)
    g5_consultas = Logs.objects.filter(error=True).values('modulo').annotate(total_errores=Count('id'))
    g5_labels = [item['modulo'] for item in g5_consultas]
    g5_data = [item['total_errores'] for item in g5_consultas]

    json_completo = {
        "ingresos_metodo": {
            "labels": g1_labels,
            "data": g1_data,
            "titulo": "Distribución de Ingresos por Método de Pago ($)"
        },
        "clientes_estado": {
            "labels": g2_labels,
            "data": g2_data,
            "titulo": "Estado Actual de la Base de Clientes"
        },
        "planes_populares": {
            "labels": g3_labels,
            "data": g3_data,
            "titulo": "Planes de Internet más Vendidos"
        },
        "ingresos_mensuales": {
            "labels": g4_labels,
            "data": g4_data,
            "titulo": "Evolución de Ingresos Mensuales ($)"
        },
        "metricas_logs": {
            "labels": g5_labels,
            "data": g5_data,
            "titulo": "Cantidad de Errores Detectados por Módulo"
        }
    }

    return JsonResponse(json_completo)