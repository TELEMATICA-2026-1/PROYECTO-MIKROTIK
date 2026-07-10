from django.urls import path
from .views import gestion_reportes, api_datos_reportes, descargar_reporte_pdf

urlpatterns = [
    path('gestion_reportes/', gestion_reportes, name='gestion_reportes'),
    path('api/datos-reportes/', api_datos_reportes, name='api_datos_reportes'),
    path('descargar-pdf/', descargar_reporte_pdf, name='descargar_reporte_pdf'),
]