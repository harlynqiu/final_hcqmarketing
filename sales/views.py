from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SaleForm, SaleItemFormSet
from .models import Sale, SaleItem
from inventory.models import Product  # Assuming the product model is in the inventory app

def index(request):
    """
    View to display a list of all sales.
    """
    sales = Sale.objects.all()
    return render(request, 'sales/index.html', {'sales': sales})

def add(request):
    """
    View to create a new sales order.
    """
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)

        if sale_form.is_valid() and formset.is_valid():
            # Save the sale
            sale = sale_form.save()

            # Save the sale items and update inventory
            items = formset.save(commit=False)
            for item in items:
                item.sale = sale
                item.save()

                # Update inventory stock and check if there's enough stock
                product = item.product
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save()
                else:
                    # If not enough stock, roll back the sale and show an error message
                    sale.delete()  # Optionally delete the sale to prevent inconsistencies
                    messages.error(request, f'Not enough stock for {product.product_name}. Sale could not be completed.')
                    return redirect('sales_add')  # Redirect to the add page again

            messages.success(request, 'Sale created successfully!')
            return redirect('sales_index')  # Redirect to the sales list
        else:
            messages.error(request, 'There were errors in your form submission.')

    else:
        sale_form = SaleForm()
        formset = SaleItemFormSet()

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
    })
