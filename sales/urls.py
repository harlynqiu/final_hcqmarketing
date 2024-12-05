from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # List of all sales
    path('sales/', views.sales_list, name='sales_list'),  # Access sales at root of the sales section

    # Create a new sale
    path('create/', views.create_sale, name='create_sale'),

    # Walk-in customer sales page (for new walk-in customers)
    path('walk-in/', views.walk_in_sale, name='walk_in_sale'),  # Handle walk-in customer sales

    # Edit sale
    path('edit/<int:sale_id>/', views.edit_sale, name='edit_sale'),

    # Delete sale
    path('<int:pk>/delete/', views.delete_sale, name='delete_sale'),

    # Fetch products for the sale
    path('get-products/', views.get_products, name='get_products'),

    # Sale detail view, which should display detailed info about a specific sale
    path('details/<int:sale_id>/', views.sales_detail, name='sales_detail'),  # Ensure this is below other paths to avoid conflict

    #invoice
    path('sales/<int:sale_id>/add-invoice/', views.add_invoice, name='add_invoice'),

    # Update sale items (e.g., edit products in a sale)
    path('<int:sale_id>/update_items/', views.update_sale_items, name='update_sale_items'),

    # Delete a sale item
    path('sales/<int:sale_id>/delete_item/<int:item_id>/', views.delete_sale_item, name='delete_sale_item'),

    #change sales status
    path('<int:pk>/change-status/', views.change_sales_status, name='change_sales_status'),

    path('sales-return/create/<int:sale_id>/', views.create_sales_return, name='create_sales_return'),  # Create a sales return
    path('sales-return/list/', views.sales_return_list, name='sales_return_list'),  # List of sales returns
]

