from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.forms import modelformset_factory
from django.contrib import messages
from .models import Sales, SalesItem, Customer, Product
from .forms import SalesForm, SalesItemForm

# Create Sale
def create_sale(request):
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=1, can_delete=True)  # Allow deletion of formset items
    sale_form = SalesForm(request.POST or None)
    formset = SaleItemFormSet(request.POST or None, queryset=SalesItem.objects.none())  # Initialize empty formset
    customers = Customer.objects.all()

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            # Save sale instance
            sale = sale_form.save(commit=False)
            sale.save()

            # Process each form in the formset
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):  # Ensure valid and not marked for deletion
                    sale_item = form.save(commit=False)
                    sale_item.sales = sale  # Link sale_item to the sale
                    sale_item.save()

            # Update the total cost
            sale.total_cost = sum(item.price_per_unit * item.quantity for item in sale.salesitem_set.all())
            sale.save()

            messages.success(request, 'Sale has been successfully created!')
            return redirect('sales_list')  # Redirect to sales list

        else:
            messages.error(request, 'There was an error creating the sale. Please check the details.')

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
        'customers': customers,
    })

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

            # Update the total cost
            sale.total_cost = sum(item.price_per_unit * item.quantity for item in sale.salesitem_set.all())
            sale.save()

            messages.success(request, 'Sale has been updated successfully!')
            return redirect('sales_list')

        else:
            messages.error(request, 'There was an error updating the sale. Please check the details.')

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
        'products': Product.objects.all(),
        'sale': sale,
    })

# Delete Sale
def delete_sale(request, pk):
    sale = get_object_or_404(Sales, pk=pk)
    sale.delete()
    messages.success(request, 'Sale has been successfully deleted!')
    return redirect('sales_list')  # Redirect after successful deletion
