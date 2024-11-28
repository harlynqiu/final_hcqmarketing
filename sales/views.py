from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Sales, SalesItem, Customer, Product
from .forms import SalesForm, SalesItemForm
from django.forms import modelformset_factory
from django.contrib import messages

# Create Sales
def create_sale(request):
    sale_form = SalesForm(request.POST or None)
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=1)

    customers = Customer.objects.all()  # Ensure all customers are retrieved

    if request.method == 'POST':
        if sale_form.is_valid():
            sale = sale_form.save(commit=False)
            sale.save()

            formset = SaleItemFormSet(request.POST)
            if formset.is_valid():
                for form in formset:
                    sale_item = form.save(commit=False)
                    sale_item.sales = sale
                    sale_item.save()

                # Calculate the total cost
                sale.total_cost = sum(item.price_per_unit * item.quantity for item in sale.salesitem_set.all())
                sale.save()

                messages.success(request, 'Sale has been successfully created!')
                return redirect('sales_list')  # Redirect to the sales list view

    else:
        formset = SaleItemFormSet(queryset=SalesItem.objects.none())

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
        'customers': customers  # Pass the customers here
    })

# List of all Sales
def sales_list(request):
    sales = Sales.objects.all()  # Get all sales
    return render(request, 'sales/index.html', {
        'sales': sales
    })

# Edit Sales (Optional: if you want to allow editing of existing sales)
def edit_sale(request, sale_id):
    sale = Sales.objects.get(id=sale_id)
    sale_form = SalesForm(request.POST or None, instance=sale)

    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, queryset=SalesItem.objects.filter(sales=sale))

    if request.method == 'POST':
        if sale_form.is_valid():
            sale = sale_form.save(commit=False)
            sale.save()

            formset = SaleItemFormSet(request.POST)
            if formset.is_valid():
                for form in formset:
                    sale_item = form.save(commit=False)
                    sale_item.sales = sale  # Ensure correct relationship
                    sale_item.save()

                # Calculate new total cost
                sale.total_cost = sum(item.price_per_unit * item.quantity for item in sale.salesitem_set.all())
                sale.save()

                messages.success(request, 'Sale has been updated successfully!')
                return redirect('sales_list')  # Redirect to the sales list view
            else:
                messages.error(request, 'There was an error with the product details.')
        else:
            messages.error(request, 'There was an error with the sale details.')

    else:
        formset = SaleItemFormSet(queryset=SalesItem.objects.filter(sales=sale))

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
        'products': Product.objects.all(),
        'sale': sale
    })
