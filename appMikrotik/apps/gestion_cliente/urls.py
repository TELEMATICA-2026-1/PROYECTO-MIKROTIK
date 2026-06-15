from django.urls import path
from . import views

# Este archivo define las rutas URL para la aplicación de gestión de clientes, 
# incluyendo las rutas para mostrar la lista de pagos, crear un nuevo cliente, modificar un cliente existente, 
# borrar a un cliente existente y mostrar la lista de clientes . 
# Cada ruta está asociada a una vista correspondiente que maneja la lógica de cada funcionalidad.

urlpatterns = [
    path('gestion_cliente/', views.gestion_cliente, name='gestion_clientes'),
    path('crear_cliente/', views.crear_cliente, name='crear_cliente'),
    path('modificar_cliente/<int:id>/', views.modificar_cliente, name='modificar_cliente'),
    path('borrar_cliente/<int:id>/', views.borrar_cliente, name='confirmar_borrado'),
    path('api/tarjetas-dashboard/', views.api_tarjetas_dashboard, name='api_tarjetas_dashboard'),
    path('api/graficos-dashboard/', views.api_graficos_dashboard, name='api_graficos_dashboard'),
    path('detalles_cliente/<int:id>/', views.detalles_cliente, name='detalles_cliente')
]