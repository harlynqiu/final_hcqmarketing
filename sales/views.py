from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import JsonResponse

from inventory.models import Inventory

from .models import Sales, SalesItem, Customer, Product
from .forms import SalesForm, SalesItemForm, SalesItemFormSet

# Create Sale
def create_sale(request):
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=1, can_delete=True)

    sale_form = SalesForm(request.POST or None)
    formset = SaleItemFormSet(request.POST or None, queryset=SalesItem.objects.none())  # Initialize formset with empty query

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            # Save sale instance
            sale = sale_form.save(commit=False)
            sale.payment_stat = 'Pending'  # Default payment status
            sale.save()  # Save the sale first to get a primary key for the sale instance

            # Process each form in the formset
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):  # Check if not marked for deletion
                    sale_item = form.save(commit=False)
                    sale_item.sale = sale  # Assign the sale instance to the SalesItem
                    
                    # Debugging check to print price and quantity before saving
                    print(f"Price per item: {sale_item.price_per_item}, Quantity: {sale_item.quantity}")
                    
                    # Modify validation to allow saving if price_per_item and quantity are zero
                    if sale_item.price_per_item is not None and sale_item.quantity is not None:
                        sale_item.save()  # Save the SalesItem
                    else:
                        print("Invalid data for sale item, not saving.")  # Optional: for debugging invalid data

            # Update the total amount for the sale using related_name 'items'
            total_amount = 0
            for item in sale.items.all():
                # Ensure both price_per_item and quantity are valid
                if item.price_per_item is not None and item.quantity is not None:
                    total_amount += item.price_per_item * item.quantity

            sale.total_amount = total_amount
            sale.save()  # Save the updated total amount

            messages.success(request, 'Sale has been successfully created!')
            return redirect('sales:sales_list')  # Redirect to sales list after successful creation
        else:
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

def get_products(request):
    products = Product.objects.all()
    product_data = [{"id": product.id, "name": product.product_name, "price": float(product.product_price)} for product in products]
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
            return redirect('sales:sales_list')

        else:
            print("Sale Form Errors:", sale_form.errors)
            print("Formset Errors:", formset.errors)
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
    return redirect('sales:sales_list')  # Redirect after successful deletion

def sales_detail(request, sale_id):                                                                                    #recently added
    sale = get_object_or_404(Sales, id=sale_id)
    sales_form = SalesForm(request.POST or None, instance=sale)
    sales_item_formset = SalesItemFormSet(request.POST or None, queryset=sale.items.all())

    if request.method == "POST":
        if sales_form.is_valid() and sales_item_formset.is_valid():
            # Save sale instance
            sales_form.save()
            # Save sale items from the formset
            sales_item_formset.save()

            # Update total amount
            sale.total_amount = sum(item.price_per_item * item.quantity for item in sale.items.all())
            sale.save()

            messages.success(request, "Sale updated successfully!")
            return redirect('sales:sales_detail', sale_id=sale.id)

    return render(request, "sales/sales_detail.html", {
        "sale": sale,
        "sales_form": sales_form,
        "sales_item_formset": sales_item_formset,
    })

def update_sale_items(request, sale_id):                                                                    #recently added
    sale = get_object_or_404(Sales, id=sale_id)
    sales_item_formset = SalesItemFormSet(request.POST or None, queryset=sale.items.all())

    if request.method == "POST":
        if sales_item_formset.is_valid():
            sales_item_formset.save()
            # Optionally, update the total amount for the sale
            sale.total_amount = sum(item.price_per_item * item.quantity for item in sale.items.all())
            sale.save()
            messages.success(request, "Sale items updated successfully!")
            return redirect('sales:sales_detail', sale_id=sale.id)

        else:
            messages.error(request, "There was an error updating the sale items.")

    return render(request, "sales/sales_detail.html", {
        "sale": sale,
        "sales_item_formset": sales_item_formset,
    })

