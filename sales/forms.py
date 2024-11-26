from django import forms
from django.apps import apps
from .models import Sale, SaleItem
from django.forms import modelformset_factory

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer_name', 'status']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'price_per_unit']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'required': 'required'
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use apps.get_model to avoid circular import issues
        Product = apps.get_model('inventory', 'Product')
        self.fields['product'].queryset = Product.objects.all()

# Inline formset for handling multiple SaleItems
SaleItemFormSet = modelformset_factory(
    SaleItem,
    fields=('product', 'quantity', 'price_per_unit'),
    extra=1
)
