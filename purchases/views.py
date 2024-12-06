from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from .models import Purchase, PurchaseItem, PurchaseReturn, PurchaseReturnItem, Invoice
from .forms import PurchaseForm, PurchaseItemFormSet, InvoiceForm, PurchaseReturnForm, PurchaseReturnItemFormSet
from suppliers.models import Supplier
from inventory.models import Inventory, StockHistory, SerializedInventory

def update_inventory_for_item(item, added_quantity, reverse=False):
    """Adjust the inventory stock based on the delivered quantity."""
    inventory = item.inventory
    if reverse:
        # Subtract the delivered quantity to revert the change
        inventory.inventory_stock -= item.delivered_quantity
    else:
        # Add the newly delivered quantity
        inventory.inventory_stock += added_quantity
    inventory.save()

def log_stock_history(item, status, remarks, quantity):
    """Log stock history for the item."""
    StockHistory.objects.create(
        inventory=item.inventory,
        purchase=item.purchase,
        status=status,
        delivered_quantity=quantity,
        remarks=remarks
    )

def add_purchase(request):
    if request.method == "POST":
        purchase_form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST, queryset=PurchaseItem.objects.none())

        if purchase_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    purchase = purchase_form.save(commit=False)
                    purchase.status = 'Pending'
                    
                    today = datetime.now().strftime("%Y%m%d")
                    latest_purchase = Purchase.objects.filter(purchase_code__startswith=f"PUR-{today}").order_by("id").last()
                    next_number = 1 if not latest_purchase else int(latest_purchase.purchase_code.split('-')[-1]) + 1
                    purchase.purchase_code = f"PUR-{today}-{next_number:03d}"
                    purchase.save()

                    total_cost = 0
                    purchase_items = []
                    for form in formset:
                        purchase_item = form.save(commit=False)
                        purchase_item.purchase = purchase
                        if not purchase_item.price:
                            purchase_item.price = purchase_item.inventory.product.purchase_price
                        purchase_item.save()
                        purchase_items.append(purchase_item)
                        total_cost += purchase_item.quantity * purchase_item.price

                    purchase.total_cost = total_cost
                    purchase.save()

                messages.success(request, f"Purchase {purchase.purchase_code} created successfully with status 'Pending'.")
                return redirect('purchases:purchase_index')

            except IntegrityError as e:
                messages.error(request, f"Error saving purchase: {e}")
        else:
            messages.error(request, "There was an error with the form submission.")

    else:
        purchase_form = PurchaseForm()
        formset = PurchaseItemFormSet(queryset=PurchaseItem.objects.none())

    suppliers = Supplier.objects.all()
    inventories = Inventory.objects.all()

    return render(request, 'purchases/add_purchase.html', {
        'purchase_form': purchase_form,
        'formset': formset,
        'suppliers': suppliers,
        'inventories': inventories,
    })

def change_purchase_status(request, purchase_id):
    # Get the purchase object by its ID
    purchase = get_object_or_404(Purchase, id=purchase_id)

    if request.method == "POST":
        # Get the new status from the form submission
        new_status = request.POST.get('status')

        # Update the purchase status
        purchase.status = new_status
        purchase.save()

        # Handle stock updates only when the status is 'Delivered'
        if new_status == 'Delivered':
            # Iterate over the items in the purchase
            for item in purchase.items.all():
                # Calculate the delivered quantity for the item
                delivered_quantity = item.quantity - item.delivered_quantity
                if delivered_quantity > 0:
                    # Update the delivered quantity
                    item.delivered_quantity += delivered_quantity
                    item.save()

                    # Adjust the inventory stock
                    inventory_item = item.inventory
                    inventory_item.inventory_stock -= delivered_quantity  # Deduct from stock

                    inventory_item.save()

            # Add a success message to notify the user
            messages.success(request, "Purchase status updated to 'Delivered' and stock has been adjusted.")

        else:
            # Handle non-stock updating status changes if needed (e.g., 'Pending', 'Partially Delivered', etc.)
            messages.info(request, f"Purchase status updated to '{new_status}'.")

        # Redirect to the purchase detail page or any other page you want
        return redirect('purchases:purchase_index')

    return render(request, 'purchases/change_status.html', {'purchase': purchase})

def add_invoice(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)

    if request.method == 'POST':
        invoice_number = request.POST.get('invoice_number')
        invoice_date = request.POST.get('invoice_date')
        shipment_date = request.POST.get('shipment_date')
        remarks = request.POST.get('remarks')

        invoice = Invoice.objects.create(
            purchase=purchase,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            shipment_date=shipment_date,
            remarks=remarks,
        )
        
        return redirect('purchases:purchase_detail', purchase_id=purchase.id)

    return render(request, 'purchases/add_invoice.html', {'purchase': purchase})

def purchase_return_list(request):
    returns = PurchaseReturn.objects.all().order_by('-return_date')
    return render(request, 'purchases/purchase_return.html', {'returns': returns})

def update_inventory_for_returned_item(item, returned_quantity):
    """Adjust the inventory stock based on the returned quantity."""
    inventory = item.item.inventory
    inventory.inventory_stock -= returned_quantity  # Reduce stock for returned items
    inventory.save()

def log_return_stock_history(item, returned_quantity):
    """Log stock history for the returned items."""
    StockHistory.objects.create(
        inventory=item.item.inventory,
        purchase=item.item.purchase,
        status='Returned',
        delivered_quantity=-returned_quantity,  # Negative for returns
        remarks=f"Returned {returned_quantity} units."
    )

def create_purchase_return(request):
    if request.method == 'POST':
        purchase_return_form = PurchaseReturnForm(request.POST)
        purchase = None

        if purchase_return_form.is_valid():
            purchase = purchase_return_form.cleaned_data.get('purchase')

        formset = PurchaseReturnItemFormSet(request.POST, form_kwargs={'purchase': purchase})

        if formset.is_valid():
            try:
                with transaction.atomic():
                    purchase_return = purchase_return_form.save(commit=False)
                    purchase_return.save()

                    total_returned_cost = 0
                    for form in formset:
                        return_item = form.save(commit=False)
                        return_item.purchase_return = purchase_return
                        return_item.save()

                        # Adjust inventory and log return history
                        update_inventory_for_returned_item(return_item, return_item.returned_quantity)
                        log_return_stock_history(return_item, return_item.returned_quantity)

                        total_returned_cost += return_item.returned_quantity * return_item.item.price

                    purchase_return.total_returned_cost = total_returned_cost
                    purchase_return.save()

                    messages.success(request, f"Purchase return {purchase_return.id} created successfully.")
                    return redirect('purchases:purchase_return_list')
            except Exception as e:
                messages.error(request, f"Error creating purchase return: {e}")

    else:
        purchase_return_form = PurchaseReturnForm()
        formset = PurchaseReturnItemFormSet(queryset=PurchaseReturnItem.objects.none())

    return render(request, 'purchases/create_purchase_return.html', {
        'purchase_return_form': purchase_return_form,
        'formset': formset
    })

def purchase_index(request):
    # Get all purchases or filter based on a condition
    purchases = Purchase.objects.all()

    # Add product_count for each purchase
    for purchase in purchases:
        purchase.product_count = sum(item.quantity for item in purchase.items.all())

    return render(request, 'purchases/index.html', {'purchases': purchases})



def purchase_detail(request, purchase_id):
    # Fetch the purchase object using the purchase_id
    purchase = get_object_or_404(Purchase, id=purchase_id)

    # Fetch the associated invoice if the status is "Delivered"
    invoice = None
    if purchase.status == 'Delivered':
        try:
            invoice = Invoice.objects.get(purchase=purchase)
        except Invoice.DoesNotExist:
            invoice = None

    return render(request, 'purchases/purchase_detail.html', {
        'purchase': purchase,
        'invoice': invoice
    })

def get_items_for_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    items = purchase.items.filter(delivered_quantity__gt=0)  # Ensure items have delivered quantity

    data = {
        "items": [
            {
                "id": item.id,
                "name": item.inventory.product.product_name,
                "delivered_quantity": item.delivered_quantity,  # Confirm correct field name
            }
            for item in items
        ]
    }

    return JsonResponse(data)