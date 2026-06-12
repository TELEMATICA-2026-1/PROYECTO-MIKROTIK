from django.forms import ModelForm, forms, BooleanField
from core.models import Cliente, Plan
from django.forms.widgets import CheckboxInput, Select
import re 
from django import forms

class PlanSelectWidget(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index,
            subindex=subindex, attrs=attrs
        )
        if value not in (None, ''):
            actual_value = getattr(value, 'value', value)
            try:
                plan = Plan.objects.get(pk=actual_value)
                option['attrs']['data-preciousd'] = str(plan.precioUSD)
                option['attrs']['data-velocidad-subida'] = str(plan.velocidad_subida)
                option['attrs']['data-velocidad-bajada'] = str(plan.velocidad_bajada)
            except (Plan.DoesNotExist, TypeError, ValueError):
                pass
        return option

# Este archivo define los formularios utilizados en la gestión de clientes, incluyendo el formulario para registrar y modificar pagos,
# tambien trae las validaciones de los campos de la cedula, celular, direccion y que no se repitan datos de clientes existentes
# así como los formularios de filtro para la lista de clientes
class ClienteForm(ModelForm):
    
    exonerar_cliente = BooleanField(
        required=False,
        widget= CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=False
    )

    class Meta:
        model = Cliente
        fields = ['idPlan', 'nombre', 'cedula', 'celular', 'direccion', 'email', 'direccionIP']
        widgets = {
            'idPlan': PlanSelectWidget(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control','inputmode': 'numeric'}),
            'celular': forms.TextInput(attrs={'class': 'form-control','inputmode': 'numeric'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccionIP': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['exonerar_cliente'].initial = (self.instance.estado == 'Exonerado')    


    def clean_cedula(self):
            
        cedula = self.cleaned_data.get('cedula')
        
        cedula_limpio = re.sub(r'[-.\s]', '', str(cedula))
        
        if not cedula_limpio.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")
            
        if not (6 <= len(cedula_limpio) <= 9):
            raise forms.ValidationError("La cédula debe tener una longitud válida (entre 6 y 9 dígitos), ejemplo 30759412.")
        
        return cedula_limpio


    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        
        celular_limpio = re.sub(r'[-.\s()+=]', '', str(celular))

        if not celular_limpio.isdigit():
            raise forms.ValidationError("El número de celular debe contener solo números.")
            
        if len(celular_limpio) != 11:
            raise forms.ValidationError("El número celular debe tener exactamente 11 dígitos (Ej: 04141234567).")
        
        return celular_limpio


    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')

        if direccion:
            
            direccion = direccion.strip().upper()  
            
            if len(direccion) < 15:
                raise forms.ValidationError("Por favor, introduce una dirección más detallada para el equipo técnico (mínimo 15 caracteres).")
        
        return direccion
    
    def clean(self):
        cleaned_data = super().clean()
        
        campos_unicos = ['cedula', 'email', 'direccionIP', 'celular']
        
        for nombre_campo in campos_unicos:
            valor = cleaned_data.get(nombre_campo)
            
            if valor:
                filtros = {
                    nombre_campo: valor,
                    'borrado': False
                }
                consulta = Cliente.objects.filter(**filtros)
                
                if self.instance and self.instance.pk:
                    consulta = consulta.exclude(pk=self.instance.pk)
                
                if consulta.exists():
                    self.add_error(
                        nombre_campo, 
                        f"{nombre_campo} ya pertenece a un cliente activo en el sistema."
                    )
        
        return cleaned_data

class FiltroClientes(forms.Form):
    nombreCliente = forms.CharField(label='Buscar Cliente', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Nombre o RIF del cliente', 'class': 'form-control tabla-input'}))
    OPCIONES_ESTADO = [('', 'Todos')] + Cliente.SeleccionEstado.choices
    estado = forms.ChoiceField(choices=OPCIONES_ESTADO, required=False, widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))