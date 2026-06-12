from django.urls import path
from . import views

urlpatterns = [
    path('gestion_cliente/<int:id>', views.gestion_cliente, name='gestion_clientes'),
    path('crear_cliente/', views.crear_cliente, name='crear_cliente'),
    path('modificar_cliente/<int:id>/', views.modificar_cliente, name='modificar_cliente'),
    path('borrar_cliente/<int:id>/', views.borrar_cliente, name='confirmar_borrado'),
    path('api/tarjetas-dashboard/', views.api_tarjetas_dashboard, name='api_tarjetas_dashboard'),
    path('api/graficos-dashboard/', views.api_graficos_dashboard, name='api_graficos_dashboard'),
]