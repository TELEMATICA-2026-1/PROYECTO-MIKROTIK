# Las urls de una aplicacion especifican y definen las direcciones web (rutas) que los usuarios pueden navegar en la pgweb
# cada url se asocia a una vista para renderizar el contenido adecuado, 
# es decir que es el que permite que el usuario dirija el sistema a la logica adecuada

from django.urls import path   
from . import views

urlpatterns = [
    path('calcular/', views.calcular, name='calcular'),
]