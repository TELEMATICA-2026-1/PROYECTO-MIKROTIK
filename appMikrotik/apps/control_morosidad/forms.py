from django import forms
from .models import ConfiguracionMorosidad

class ConfiguracionMorosidadForm(forms.ModelForm):
    # Formulario creado para que el administrador configure los parametros de morosidad
    class Meta:
        model = ConfiguracionMorosidad
        fields = ['diasGracia','diaCobroMensual']
        widgets={
            'diasGracia': forms.NumberInput(attrs={'class': 'form-control'}),
            'diaCobroMensual': forms.NumberInput(attrs={'class': 'form-control', 'min':1, 'max':28}),
        }