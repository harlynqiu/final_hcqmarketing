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
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_stat': forms.Select(attrs={'class': 'form-select'}),
        }

        customer = forms.ModelChoiceField(
            queryset=Customer.objects.all(),  # Ensure queryset pulls from Customer model
            empty_label="Select Customer",
            widget=forms.Select(attrs={'class': 'form-control'})
        )


# SalesItem Form for each product in the sale
class SalesItemForm(forms.ModelForm):
    class Meta:
        model = SalesItem
        fields = ['product', 'quantity', 'price_per_item']  # Include any other necessary fields

    # Customizing form fields if needed
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    price_per_item = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

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
