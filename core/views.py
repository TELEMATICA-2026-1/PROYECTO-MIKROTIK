
from django.shortcuts import render
from .models import Operacion
from .forms import FormCalculadora

## en django las vistas son estructuras o clases que reciben las solicitudes http y devuelven las respuestas
# Aunque su nombre puede presentar confusion si se viene de MVC clasico, estas vistas encargan de procesar la logica de negiocio y interactuar con los modelos para obtener o modificar datos
# cada funcion de vista recibe un objeto request que contiene toda la informacion de la solicitud http;
# como los datos del formulario o informacion que se necesita y devuelve una respuesta http, que puede ser una pagina web, un redireccionamiento hacia otra vista, un mensaje de error entre otros

def calcular(request):
    resultado = None
    form = FormCalculadora(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            num1 = float(form.cleaned_data['numero1'])
            num2 = float(form.cleaned_data['numero2'])
            op = form.cleaned_data['operacion']

             # creamos un diccionario para mapear las posibles operaciones a sus resultados 
             #usar el diccionario para mapear la operacion con el diccionario es mas limpio y facil de mantener que condicionales
            switcher = {
                'sumar': num1 + num2,
                'restar': num1 - num2,
                'multiplicar': num1 * num2,
                'dividir': num1 / num2 if num2 != 0 else 'no se puede dividir por cero'
            }

            resultado = switcher.get(op, 'operacion no valida')
            
            # hacemos un registro de la operación realizada en la BD utilizando el modelo Operacion
            # Operacion.objects.create(numero1=num1, numero2=num2, operacion=op, resultado=resultado)
        
        else:
            return render(request, 'core/calcular.html', {'form': form, 'error': 'Formulario no válido'})
        
    # renderizamos la plantilla index.html y le pasamos el resultado de la operación para mostrarlo en la pgweb
    return render(request, 'core/calcular.html', {'resultado': resultado})