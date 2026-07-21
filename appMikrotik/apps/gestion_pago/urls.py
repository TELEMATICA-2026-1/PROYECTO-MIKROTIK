from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# Este archivo define las rutas URL para la aplicación de gestión de pagos, 
# incluyendo las rutas para mostrar la lista de pagos, crear un nuevo pago, modificar un pago existente, 
# mostrar los detalles de un pago específico y mostrar la lista de clientes con pagos pendientes. 
# Cada ruta está asociada a una vista correspondiente que maneja la lógica de cada funcionalidad.

urlpatterns = [
    path('gestion_pagos/<int:id>/', views.gestion_pago, name='gestion_pagos'),
    path('crear_pago/<int:id>/', views.crear_pago, name='crear_pago'),
    path('modificar_pago/<int:id>/', views.modificar_pago, name='modificar_pago'),
    path('detalles_pago/<int:id>/', views.mostrar_detalles, name='detalles_pago'),
    path('pendientes/', views.pendientes, name='pagos_pendientes'),
    path('gestion_pagos/exportar/<int:id>/', views.exportar_pagos_excel, name='exportar_pagos_excel'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 