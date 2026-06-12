import routeros_api
from django.conf import settings
from .models import Logs
from django.contrib.auth.models import User
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError

def obtenerConexionMikroti():
    """Retorna una conexion API al router Mikrotik usando la 
    libreria routeros-api"""
    try:
        conexion = routeros_api.RouterOsApiPool(
            settings.MIKROTIK_HOST,
            username=settings.MIKROTIK_USER,
            password=settings.MIKROTIK_PASSWORD,
            port=settings.MIKROTIK_PORT,
            use_ssl=False,
            plaintext_login=True
        )
        api = conexion.get_api()
        return api, conexion
    except Exception as e:
        usuarioSistema, _ = User.objects.get_or_create(username='system')
        Logs.objects.create(
            idPersonal= usuarioSistema,
            modulo='Mikrotik',
            mensaje= f'error al conectar con el router: {str(e)}',
            error =True
        )
        raise e

def suspenderCliente(direccionIp):
    try:
        validate_ipv4_address(direccionIp)
    except ValidationError:
        raise ValueError(f"La dirección {direccionIp} no tiene un formato IPv4 válido.")
    if not direccionIp or str(direccionIp).strip() == "":
        raise ValueError("La dirección IP no puede estar vacía")
        
    # Aplica una regla de firewall para bloquear una IP especifica 
    api, conexion = obtenerConexionMikroti()
    try:
        listaDirecciones= api.get_resource('/ip/firewall/address-list')
        existente = listaDirecciones.get(list='suspendidos', address=direccionIp)
        if not existente:
            listaDirecciones.add(list='suspendidos', address=direccionIp, comment='Suspendido por morosidad')
        return True
    except Exception as e:
        raise e
    finally:
        conexion.disconnect()

def reconectarCliente(direccionIp):
    try:
        validate_ipv4_address(direccionIp)
    except ValidationError:
        raise ValueError(f"La dirección {direccionIp} no tiene un formato IPv4 válido.")
    if not direccionIp or str(direccionIp).strip() == "":
        raise ValueError("La dirección IP no puede estar vacía")

    #Elimina la regla de firewall que bloqueaba a la IP especifica
    api, conexion = obtenerConexionMikroti()
    try:
        listaDirecciones = api.get_resource('/ip/firewall/address-list')
        items = listaDirecciones.get(list='suspendidos', address=direccionIp)
        for item in items:
            listaDirecciones.remove(id=item['id'])
        return True
    except Exception as e:
        raise e
    finally:
        conexion.disconnect()
        



