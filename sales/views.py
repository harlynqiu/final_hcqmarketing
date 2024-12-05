from datetime import timedelta, timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import SalesReturnForm, SalesForm, SalesItemForm, SalesItemFormSet
from inventory.models import Inventory
from django.utils import timezone
from .models import Sales, SalesItem, Customer, Product, Invoice, SalesReturn

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

            # Now that the sale has a primary key, calculate the total amount for the sale
            total_amount = 0
            for item in sale.items.all():  # Access sale items after saving the sale
                if item.price_per_item is not None and item.quantity is not None:
                    total_amount += item.price_per_item * item.quantity

            sale.total_amount = total_amount
            sale.save()  # Save the updated total amount

            # Process each form in the formset
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):  # Check if not marked for deletion
                    sale_item = form.save(commit=False)
                    sale_item.sale = sale  # Assign the sale instance to the SalesItem
                    if sale_item.price_per_item is not None and sale_item.quantity is not None:
                        sale_item.save()  # Save the SalesItem
                    else:
                        print("Invalid data for sale item, not saving.")  # Optional: for debugging invalid data

            # Update Inventory Stock
            for item in sale.items.all():  # Loop through sale items
                product = item.product
                quantity_sold = item.quantity
                inventory_item = Inventory.objects.get(product=product)
                inventory_item.inventory_stock -= quantity_sold
                inventory_item.save()

            messages.success(request, 'Sale has been processed and inventory updated.')
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

# Walk-in Sale (for walk-in customers)
def walk_in_sale(request):
    walk_in_customer = Customer.objects.get(id=1)  # Assuming walk-in customer has id=1
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=1, can_delete=True)

    sale_form = SalesForm(request.POST or None)
    formset = SaleItemFormSet(request.POST or None, queryset=SalesItem.objects.none())  # Initialize formset with empty query

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            # Save sale instance for walk-in customer
            sale = sale_form.save(commit=False)
            sale.customer = walk_in_customer  # Assign the walk-in customer
            sale.payment_stat = 'Pending'  # Default payment status
            sale.save()  # Save the sale first to get a primary key for the sale instance

            # Process each form in the formset
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):  # Check if not marked for deletion
                    sale_item = form.save(commit=False)
                    sale_item.sale = sale  # Assign the sale instance to the SalesItem
                    if sale_item.price_per_item is not None and sale_item.quantity is not None:
                        sale_item.save()  # Save the SalesItem
                    else:
                        print("Invalid data for sale item, not saving.")  # Optional: for debugging invalid data

            # Update the total amount for the sale using related_name 'items'
            total_amount = 0
            for item in sale.items.all():
                if item.price_per_item is not None and item.quantity is not None:
                    total_amount += item.price_per_item * item.quantity

            sale.total_amount = total_amount
            sale.save()  # Save the updated total amount

            # Update Inventory Stock
            for item in sale.items.all():  # Loop through sale items
                product = item.product
                quantity_sold = item.quantity
                inventory_item = Inventory.objects.get(product=product)
                inventory_item.inventory_stock -= quantity_sold
                inventory_item.save()

            messages.success(request, 'Walk-in sale has been successfully created and inventory updated!')
            return redirect('sales:sales_list')  # Redirect to sales list after successful creation
        else:
            print("Sale Form Errors:", sale_form.errors)
            print("Formset Errors:", formset.errors)
            messages.error(request, 'There was an error creating the walk-in sale. Please check the details.')

    return render(request, 'sales/walk_in.html', {
        'sale_form': sale_form,
        'formset': formset,
        'products': Product.objects.all(),
    })

# Get Products for Sale
def get_products(request):
    products = Product.objects.all()  # Fetch all products
    product_list = [{'id': product.id, 'name': product.name, 'price': product.price} for product in products]
    return JsonResponse(product_list, safe=False)

# Add an Invoice to a Sale
def add_invoice(request, sale_id):
    sale = Sales.objects.get(id=sale_id)
    
    # Create the invoice object
    invoice = Invoice(
        sale=sale,
        invoice_number="INV-123456",  # Generate or fetch invoice number dynamically
        invoice_date=timezone.now().date(),
        shipment_date=timezone.now().date() + timedelta(days=7),  # Assuming 7 days for shipment
        #remarks="Optional remarks here",
    )
    
    # Save the invoice
    invoice.save()

    # Optionally, update the sale with the invoice
    sale.sales_invoice = invoice
    sale.save()

    return redirect('sales:sales_detail', sale_id=sale.id)

# Update Sale Items
def update_sale_items(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    if request.method == 'POST':
        sale_items = request.POST.getlist('sale_items')
        # Process the updates for sale items
        for item_data in sale_items:
            item_id, new_quantity = item_data.split(":")
            sale_item = SalesItem.objects.get(id=item_id)
            sale_item.quantity = int(new_quantity)
            sale_item.save()
        messages.success(request, 'Sale items updated successfully.')
        return redirect('sales:sales_detail', sale_id=sale.id)
    return render(request, 'sales/update_sale_items.html', {'sale': sale})

# Delete Sale Item
def delete_sale_item(request, sale_id, item_id):
    sale = get_object_or_404(Sales, id=sale_id)
    sale_item = get_object_or_404(SalesItem, id=item_id)
    sale_item.delete()
    messages.success(request, 'Sale item deleted successfully.')
    return redirect('sales:sales_detail', sale_id=sale.id)

# Change Sales Status
def change_sale_status(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        sale.status = new_status  # Ensure that you update the `status` field here
        sale.save()
        messages.success(request, f'Sales status changed to {new_status}.')
        return redirect('sales:sales_detail', sale_id=sale.id)
    return redirect('sales:sales_list')

# Delete Sale
def delete_sale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    sale.delete()
    messages.success(request, 'Sale deleted successfully.')
    return redirect('sales:sales_list')

# Create Sales Return
def create_sales_return(request, sale_id):
    sale = get_object_or_404(Sales, pk=sale_id)

    # Get the last return code for this sale and increment it
    last_return = SalesReturn.objects.filter(sales=sale).order_by('-id').first()
    if last_return:
        last_return_number = int(last_return.return_code[3:])  # Extract number part after 'SAR'
        new_return_code = f"SAR{last_return_number + 1:05d}"
    else:
        new_return_code = "SAR00001"  # Start with "SAR00001" if no returns exist for this sale

    if request.method == "POST":
        return_code = f"SAR{new_return_code[3:]}"  # Retain only numeric part after "SAR"
        quantity = request.POST.get('quantity')
        date = request.POST.get('date')

        # Create the sales return record
        sales_return = SalesReturn(
            return_code=new_return_code,
            sales=sale,
            quantity=quantity,
            date=date
        )
        sales_return.save()

        # Update Inventory Stock (Add returned quantity back)
        for item in sales_return.return_items.all():
            product = item.product
            quantity_returned = item.quantity
            inventory_item = Inventory.objects.get(product=product)
            inventory_item.inventory_stock += quantity_returned
            inventory_item.save()

        messages.success(request, 'Sales return processed and inventory updated.')
        return HttpResponseRedirect(reverse('sales:sales_list'))

    context = {
        'sale': sale,
        'return_code': new_return_code
    }
    return render(request, 'sales/create_sales_return.html', context)

# View to list all sales returns
def sales_return_list(request):
    returns = SalesReturn.objects.all()
    return render(request, 'sales/sales_return_list.html', {'returns': returns})

# Sales List
def sales_list(request):
    sales = Sales.objects.all()  # Retrieve all sales
    return render(request, 'sales/index.html', {
        'sales': sales,
    })

def sales_detail(request, sale_id):
    """Display detailed information about a specific sale."""
    sale = get_object_or_404(Sales, id=sale_id)  # Fetch the sale or return a 404 error if not found
    context = {
        'sale': sale,
        'items': sale.items.all(),  # Get all related sale items
    }
    return render(request, 'sales/sales_detail.html', context)
# Edit Sale
def edit_sale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)  # Get the sale to edit

    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=0, can_delete=True)  # No extra form, but allow deletion
    sale_form = SalesForm(request.POST or None, instance=sale)  # Pre-populate the form with existing sale data
    formset = SaleItemFormSet(request.POST or None, queryset=sale.items.all())  # Get existing items for the sale

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            # Save the sale form
            sale = sale_form.save(commit=False)
            sale.payment_stat = 'Pending'  # Assuming that editing doesn't change payment status
            sale.save()  # Save the updated sale instance

            # Process each form in the formset (items related to the sale)
            total_amount = 0  # Reset the total amount
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):  # Check if not marked for deletion
                    sale_item = form.save(commit=False)
                    sale_item.sale = sale  # Reassign sale item to the current sale
                    sale_item.save()  # Save the updated sale item

                    # Update total amount for the sale
                    total_amount += sale_item.price_per_item * sale_item.quantity

            sale.total_amount = total_amount  # Update total amount after changes
            sale.save()  # Save the updated total amount

            # Update Inventory based on the updated sale items
            for item in sale.items.all():  # Loop through sale items and adjust inventory stock
                product = item.product
                quantity_sold = item.quantity
                inventory_item = Inventory.objects.get(product=product)
                inventory_item.inventory_stock -= quantity_sold
                inventory_item.save()

            messages.success(request, 'Sale has been successfully updated.')
            return redirect('sales:sales_detail', sale_id=sale.id)  # Redirect to sale details page
        else:
            print("Sale Form Errors:", sale_form.errors)
            print("Formset Errors:", formset.errors)
            messages.error(request, 'There was an error updating the sale. Please check the details.')

    return render(request, 'sales/edit.html', {
        'sale_form': sale_form,
        'formset': formset,
        'sale': sale,
        'customers': Customer.objects.all(),
        'products': Product.objects.all(),
        'inventories': Inventory.objects.all(),
    })

def invoice_list(request):
    invoices = Invoice.objects.all()  # Fetch all invoices
    return render(request, 'sales/invoice_list.html', {'invoices': invoices})