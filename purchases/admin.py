from django.contrib import admin
from .models import Purchase, PurchaseItem, Invoice

# Register Purchase model
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('purchase_code', 'supplier', 'date', 'total_cost', 'status')
    list_filter = ('status', 'supplier')
    search_fields = ('purchase_code', 'supplier__name')
    ordering = ('-date',)

# Register PurchaseItem model
@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'inventory', 'quantity', 'delivered_quantity', 'price')
    search_fields = ('purchase__purchase_code', 'inventory__product__product_name')
    list_filter = ('purchase__status', 'inventory__product')

# Register Invoice model
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'invoice_date', 'cargo_name', 'cargo_number', 'shipment_date', 'status', 'purchase')
    list_filter = ('status', 'term', 'purchase__status')
    search_fields = ('invoice_number', 'purchase__purchase_code', 'cargo_name')
