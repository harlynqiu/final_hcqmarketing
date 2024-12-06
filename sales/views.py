import logging
from datetime import timedelta, timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import SalesReturnForm, SalesForm, SalesItemForm, SalesItemFormSet, WalkInCustomerForm
from inventory.models import Inventory
from django.utils import timezone
from .models import Sales, SalesItem, Customer, Product, Invoice, SalesReturn
from django.core.exceptions import ValidationError

# Set up logging
logger = logging.getLogger(__name__)

# Create Sale
def create_sale(request):
    SaleItemFormSet = modelformset_factory(SalesItem, form=SalesItemForm, extra=1, can_delete=True)
    sale_form = SalesForm(request.POST or None)
    formset = SaleItemFormSet(request.POST or None, queryset=SalesItem.objects.none())

    if request.method == 'POST':
        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save(commit=False)
            sale.payment_stat = 'Pending'  # Default payment status
            sale.save()  # Save the sale first to get a primary key for the sale instance

            total_amount = 0
            for item in sale.items.all():
                if item.price_per_item is not None and item.quantity is not None:
                    total_amount += item.price_per_item * item.quantity

            sale.total_amount = total_amount
            sale.save()

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    sale_item = form.save(commit=False)
                    sale_item.sale = sale
                    if sale_item.price_per_item is not None and sale_item.quantity is not None:
                        sale_item.save()

            for item in sale.items.all():
                product = item.product
                quantity_sold = item.quantity
                inventory_item = Inventory.objects.get(product=product)
                inventory_item.inventory_stock -= quantity_sold
                inventory_item.save()

            messages.success(request, 'Sale has been processed and inventory updated.')
            return redirect('sales:sales_list')
        else:
            messages.error(request, 'There was an error creating the sale. Please check the details.')

    return render(request, 'sales/add.html', {
        'sale_form': sale_form,
        'formset': formset,
        'customers': Customer.objects.all(),
        'products': Product.objects.all(),
        'inventories': Inventory.objects.all(),
    })

# Walk-In Sale
def walk_in_sale(request):
    if request.method == 'POST':
        form = WalkInCustomerForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            date = form.cleaned_data['date']
            status = form.cleaned_data['status']
            payment_stat = form.cleaned_data['payment_stat']
            dateStart = timezone.now()

            # Get or create the customer
            customer, created = Customer.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={'dateStart': dateStart}
            )

            # Log for debugging
            logger.info(f"Form valid - Customer: {first_name} {last_name}, Date: {date}, Status: {status}, Payment: {payment_stat}")
            
            # Create the sale
            sale = Sales.objects.create(
                customer=customer,
                date=date,
                status=status,
                payment_stat=payment_stat
            )

            # If the customer is a walk-in, store the walk-in name.
            if created:  # If the customer was created for this sale
                sale.walk_in_customer_name = f"{first_name} {last_name}"
                sale.save()


            # Process selected products and quantities from form data
            product_ids = request.POST.getlist('form-0-product')  # Get product IDs from form data
            quantities = request.POST.getlist('form-0-quantity')  # Get quantities from form data

            # Iterate through each product and quantity, create a SalesItem
            for product_id, quantity in zip(product_ids, quantities):
                product = Product.objects.get(id=product_id)  # Get the product
                quantity = int(quantity)  # Convert quantity to integer

                # Create the SalesItem record for each product
                SalesItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price_per_item=product.product_price
                )

            # Update the total_amount after adding all sales items
            sale.total_amount = sale.calculate_total_amount()
            sale.save()

            # Redirect to sales list
            return redirect('sales:sales_list')
        else:
            # Log form errors if invalid
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, 'Form is invalid. Please check the entered data.')
    else:
        form = WalkInCustomerForm()

    # Pass products to the template for product selection
    products = Product.objects.all()

    return render(request, 'sales/walk_in.html', {'form': form, 'products': products})

# Get Products for Sale
def get_products(request):
    products = Product.objects.all()
    product_list = [{'id': product.id, 'name': product.product_name, 'price': product.product_price} for product in products]
    return JsonResponse(product_list, safe=False)

# Add an Invoice to a Sale
def add_invoice(request, sale_id):
    sale = Sales.objects.get(id=sale_id)
    
    invoice = Invoice(
        sale=sale,
        invoice_number="INV-123456",  # Example invoice number
        invoice_date=timezone.now().date(),
        shipment_date=timezone.now().date() + timedelta(days=7),
    )
    invoice.save()

    sale.sales_invoice = invoice
    sale.save()

    return redirect('sales:sales_detail', sale_id=sale.id)

# Update Sale Items
def update_sale_items(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    if request.method == 'POST':
        sale_items = request.POST.getlist('sale_items')
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
        sale.status = new_status
        sale.save()
        return redirect('sales:sales_detail', sale_id=sale.id)
    
    return render(request, 'sales/sales_detail.html', {'sale': sale})

# Delete Sale
def delete_sale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    sale.delete()
    messages.success(request, 'Sale deleted successfully.')
    return redirect('sales:sales_list')

# Sales List
def sales_list(request):
    sales = Sales.objects.all().order_by('-date')
    return render(request, 'sales/index.html', {'sales': sales})

# Sales Detail
def sales_detail(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    items = sale.items.all()
    return render(request, 'sales/sales_detail.html', {'sale': sale, 'items': items})

# Edit Sale
def edit_customer(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)

    if request.method == 'POST':
        customer_hardware = request.POST.get('customer_hardware')  # Get the updated customer info
        if customer_hardware:  # Check if the field is not empty
            sale.customer.customer_hardware = customer_hardware
            sale.customer.save()  # Save the updated customer details
            return redirect('sales:sale_detail', sale_id=sale.id)  # Redirect back to the sale details page

    return redirect('sales:sale_detail', sale_id=sale.id)  # Redirect if not POST (GET request or invalid form)


# Create Sales Return
def create_sales_return(request, sale_id):
    sale = get_object_or_404(Sales, pk=sale_id)
    last_return = SalesReturn.objects.filter(sales=sale).order_by('-id').first()
    if last_return:
        last_return_number = int(last_return.return_code[3:])
        new_return_code = f"SAR{last_return_number + 1:05d}"
    else:
        new_return_code = "SAR00001"

    if request.method == "POST":
        quantity = request.POST.get('quantity')
        date = request.POST.get('date')

        sales_return = SalesReturn(
            sales=sale,
            return_code=new_return_code,
            quantity=quantity,
            date=date,
        )
        sales_return.save()

        sale.status = "Returned"
        sale.save()

        return redirect('sales:sales_list')

    return render(request, 'sales/create_sales_return.html', {'sale': sale, 'return_code': new_return_code})

def sales_return_list(request):
    sales_returns = SalesReturn.objects.all().order_by('-date')
    return render(request, 'sales/sales_return_list.html', {'sales_returns': sales_returns})

# Invoice List
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-invoice_date')
    return render(request, 'sales/invoice_list.html', {'invoices': invoices})
