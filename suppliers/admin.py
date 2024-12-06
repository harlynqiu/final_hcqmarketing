from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'supplier_hardware', 'email', 'contact_num', 'status', 'dateStart', 'dateEdit')
    list_filter = ('status',)
    search_fields = ('first_name', 'last_name', 'supplier_hardware', 'email')
    ordering = ('-dateStart',)
