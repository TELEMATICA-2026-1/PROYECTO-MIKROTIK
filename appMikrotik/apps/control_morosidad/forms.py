from django import forms
from .models import ConfiguracionMorosidad

class ConfiguracionMorosidadForm(forms.ModelForm):
    # Formulario creado para que el administrador configure los parametros de morosidad
    class Meta:
        model = ConfiguracionMorosidad
        fields = ['diasGracia','diaCobroMensual']
        widgets={
            'diasGracia': forms.NumberInput(attrs={'class': 'form-control', 'min':1, 'max':30}),
            'diaCobroMensual': forms.NumberInput(attrs={'class': 'form-control', 'min':1, 'max':28}),
        }
    
    #validaciones para asegurar que los valores ingresados sean validos, aunque el widget ya limita el rango, esto es una capa adicional de seguridad
    def clean_diasGracia(self):
        diasGracia = self.cleaned_data['diasGracia']
        if diasGracia < 1 or diasGracia > 30:
            raise forms.ValidationError("Los días de gracia deben estar entre 1 y 30.")
        return diasGracia

    def clean_diaCobroMensual(self):
        diaCobroMensual = self.cleaned_data['diaCobroMensual']
        if diaCobroMensual < 1 or diaCobroMensual > 28:
            raise forms.ValidationError("El día de cobro mensual debe estar entre 1 y 28.")
        return diaCobroMensual

class FiltroClientesMorosos(forms.Form):
    nombreCliente = forms.CharField(
        label='Nombre del Cliente',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre o cédula del cliente',
            'class': 'form-control tabla-input'
        }))