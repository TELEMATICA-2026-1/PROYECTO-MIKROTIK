
# las urls del proyecto principal se encargan de enrutar las solicitudes a las aplicaciones correspondientes,
# es decir que es el punto de entrada para las solicitudes web y se encarga de dirigir

from django.contrib import admin
from django.urls import path, include 

# si tenemos muchas aplicaciones, cada una con sus propias urls:
#  es necesario incluirlas en la raiz principal para que el sistema pueda mapear y dirigir correctamente las solicitudes a cada una de ellas
# esto se hace utilizando la funcion include que permite invoca las urls de cada aplicacion en la raiz principal del proyecto 
# de esta manera se mantiene una estructura organizada y modularizada del proyecto, facilitando su escalibilidad y mantenibilidad a medida que el proyecto crece

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
