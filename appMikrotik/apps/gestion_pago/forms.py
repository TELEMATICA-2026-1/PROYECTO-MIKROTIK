from django.forms import ModelForm
from core.models import Pago
from django import forms




# Este archivo define los formularios utilizados en la gestión de pagos, incluyendo el formulario para registrar y modificar pagos,
# así como los formularios de filtro para la lista de pagos y la lista de clientes con pagos pendientes.

class PagoForm(ModelForm):
  

    class Meta:
        model = Pago
        fields = ['montoUSD', 'tasa', 'metodo', 'comprobante']
        labels = {
            'montoUSD': 'Monto a Pagar ($)',
            'tasa': 'Tasa del Día',
            'metodo': 'Método de Pago',
            'comprobante': 'Comprobante',
        }
        widgets = {
            'montoUSD': forms.TextInput(attrs={'class': 'form-control','inputmode': 'decimal'}),
            'tasa': forms.TextInput(attrs={'class': 'form-control','inputmode': 'decimal'}),
            'metodo': forms.Select(attrs={'class': 'form-select'}),
            'comprobante': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class FiltroPagos(forms.Form):
    nombreCliente = forms.CharField(label='Nombre', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Nombre o RIF', 'class': 'form-control tabla-input'}))
    fecha_inicio = forms.DateField(label='Desde', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_fin = forms.DateField(label='Hasta', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

class FiltroPendientes(forms.Form):
    nombreCliente = forms.CharField(label='Nombre o Cedula', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Nombre o RIF', 'class': 'form-control tabla-input'}))
