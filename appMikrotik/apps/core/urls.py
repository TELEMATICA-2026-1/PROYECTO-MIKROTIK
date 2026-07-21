from django.urls import path
from . import views

# Este archivo define las rutas URL para la aplicación core, 
# incluyendo las rutas para la página de inicio, 
# el inicio de sesión, el cierre de sesión y la visualización de logs del sistema. 
# Cada ruta está asociada a una vista correspondiente que maneja la lógica de cada funcionalidad.
# Incluye la ruta para descargar el reporte de los Logs en formato PDF.

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.signin, name='login'),
    path('signout/', views.signout, name='signout'),
    path('logs/', views.logs, name='logs'),
    path('logs/exportar/pdf/', views.exportar_logs_pdf, name='exportar_logs_pdf'),
]