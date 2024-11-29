from django import forms
from .models import Sales, SalesItem, Payment
from inventory.models import Product, Customer
from django.forms import modelformset_factory

# Sales Form for main sale details
class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ['customer', 'status', 'payment_stat']

        labels = {
            'customer': 'Customer Name',
            'status': 'Sale Status',
            'payment_stat': 'Payment Status',
        }

        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_stat': forms.Select(attrs={'class': 'form-control'}),
        }




class SalesItemForm(forms.ModelForm):
    class Meta:
        model = SalesItem
        fields = ['product', 'quantity', 'price_per_item']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price_per_item': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(SalesItemForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()

# Payment Form for handling payment-related details
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_method', 'payment_status']

        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
        }


# Formset for managing multiple SalesItems dynamically
SalesItemFormSet = modelformset_factory(
    SalesItem,
    form=SalesItemForm,
    extra=1,  # Number of extra empty forms to display by default
    can_delete=True  # Allow deleting items from formset
)
