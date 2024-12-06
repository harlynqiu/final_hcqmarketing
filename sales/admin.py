from django.contrib import admin
from .models import Sales, SalesItem, Invoice, SalesReturn

# Register the Sales model
@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('sales_code', 'customer', 'total_amount', 'date', 'status', 'payment_stat')
    list_filter = ('status', 'payment_stat')
    search_fields = ('sales_code', 'customer__first_name', 'customer__last_name')
    ordering = ('-date',)

# Register the SalesItem model
@admin.register(SalesItem)
class SalesItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'price_per_item', 'total_price')

# Register the Invoice model
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'invoice_date', 'shipment_date', 'sale')
    search_fields = ('invoice_number',)

# Register the SalesReturn model
@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    list_display = ('return_code', 'sales', 'quantity', 'date')
    search_fields = ('return_code',)
