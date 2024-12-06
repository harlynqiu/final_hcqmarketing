from django.contrib import admin
from .models import Employees

@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ('full_name', 'job_title', 'status', 'dateStart', 'email', 'phone')
    
    # Filter the list based on status and job title
    list_filter = ('status', 'job_title')
    
    # Add a search bar for easy searching by full name, job title, and email
    search_fields = ('full_name', 'job_title', 'email')
    
    # Default ordering of employees by date started (most recent first)
    ordering = ('-dateStart',)
    
    # Optionally, exclude certain fields from being displayed in the form
    exclude = ('phone',)  # Example of excluding phone field in the admin form
    
    # Optionally, make some fields readonly
    readonly_fields = ('email',)
    
    # You can also specify fields to be used in the form, in the order you prefer
    fields = ('full_name', 'address', 'phone', 'email', 'job_title', 'status', 'dateStart', 'emergency_name', 'emergency_contact')

