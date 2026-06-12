from django.urls import path
from . import views

urlpatterns = [
    #Panel principal de morosidad
    path('morosidad/', views.panelMorosidad, name='panelMorosidad'),
    #Vista para forzar la generacion manual de facturas
    path('morosidad/generar-facturas/', views.generarFacturasView, name='generarFacturas'),
    #Endpoint para ejecutar la rutina completa de morosidad
    path('morosidad/evaluar/', views.evaluarMorosidadView, name='evaluarMorosidad'),
]
