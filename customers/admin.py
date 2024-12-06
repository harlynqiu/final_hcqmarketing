from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'customer_hardware', 'email', 'contact_num', 'status', 'dateStart', 'startBy', 'dateEdit')
    list_filter = ('status', 'startBy')
    search_fields = ('first_name', 'last_name', 'customer_hardware', 'email')
    ordering = ('-dateStart',)
