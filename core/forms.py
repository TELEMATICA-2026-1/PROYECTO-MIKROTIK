# el archivo froms se usa para facilitar la creacion de los formularios
# automatiza la creación de campos, la validacion de datos  y la generacion de HTML
#a su vez permite una mayor integracion con las interfaces y la BD

from django import forms

class FormCalculadora(forms.Form):

    # definimos las opciones de operacion disponibles
    OPCIONES_OPERACION = [
        ('sumar', 'Sumar (+)'),
        ('restar', 'Restar (-)'),
        ('multiplicar', 'Multiplicar (x)'),
        ('dividir', 'Dividir (/)'),
    ]

    # Campos del formulario
    numero1 = forms.FloatField(label="Primer Número", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    numero2 = forms.FloatField(label="Segundo Número", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    operacion = forms.ChoiceField(
        choices=OPCIONES_OPERACION, 
        label="Operación",
        widget=forms.Select(attrs={'class': 'form-select'}) # opcional para agregar claess de css
    )
