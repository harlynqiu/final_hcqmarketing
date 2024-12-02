from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import JsonResponse

from inventory.models import Inventory

from .models import Sales, SalesItem, Customer, Product
from .forms import SalesForm, SalesItemForm

# Create Sale
def create_sale(request):
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=1, can_delete=True)

    sale_form = SalesForm(request.POST or None)
    formset = SaleItemFormSet(request.POST or None, queryset=SalesItem.objects.none())

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save(commit=False)

            # Set default payment_stat if not provided
            sale.payment_stat = 'Pending'  # Default payment status

            # Save the Sale instance
            sale.save()

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    sale_item = form.save(commit=False)
                    sale_item.sales = sale
                    sale_item.save()

            # Recalculate total
            sale.total_amount = sum(
                item.price_per_item * item.quantity for item in sale.salesitem_set.all()
            )
            sale.save()

            messages.success(request, 'Sale has been successfully created!')
            return redirect('sales_list')

        else:
            # Debug output for errors
            print("Sale Form Errors:", sale_form.errors)
            print("Formset Errors:", formset.errors)
            messages.error(request, 'There was an error creating the sale. Please check the details.')

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
        'customers': Customer.objects.all(),
        'products': Product.objects.all(),
        'inventories': Inventory.objects.all(),
    })

def save(self, *args, **kwargs):
    # Save the instance first to ensure it has a primary key
    super(Sales, self).save(*args, **kwargs)

    # Calculate total only after the instance has a primary key
    total = sum(item.total_price for item in self.items.all())
    self.total_amount = total

    # Save again to update the total_amount
    super(Sales, self).save(update_fields=["total_amount"])

def get_products(request):
    products = Product.objects.all()
    product_data = [{"id": product.id, "name": product.product_name} for product in products]
    return JsonResponse({"products": product_data})

# List of all Sales
def sales_list(request):
    sales = Sales.objects.all()  # Retrieve all sales
    return render(request, 'sales/index.html', {
        'sales': sales,
    })

# Edit Sale
def edit_sale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=0, can_delete=True)  # Editable formset
    sale_form = SalesForm(request.POST or None, instance=sale)
    formset = SaleItemFormSet(request.POST or None, queryset=SalesItem.objects.filter(sales=sale))

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            # Save the sale instance
            sale = sale_form.save(commit=False)
            sale.save()

            # Save the formset items
            for form in formset:
                if form.cleaned_data:
                    if form.cleaned_data.get('DELETE'):
                        # If marked for deletion
                        form.instance.delete()
                    else:
                        sale_item = form.save(commit=False)
                        sale_item.sales = sale
                        sale_item.save()

            # Update the total amount for the sale after the changes
            sale.total_amount = sum(item.price_per_item * item.quantity for item in sale.salesitem_set.all())
            sale.save()

            messages.success(request, 'Sale has been updated successfully!')
            return redirect('sales_list')

        else:
            messages.error(request, 'There was an error updating the sale. Please check the details.')

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
        'products': Product.objects.all(),  # Ensure products are available in the edit view
        'sale': sale,
    })

# Delete Sale
def delete_sale(request, pk):
    sale = get_object_or_404(Sales, pk=pk)
    sale.delete()
    messages.success(request, 'Sale has been successfully deleted!')
    return redirect('sales_list')  # Redirect after successful deletion