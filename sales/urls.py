from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # List of all sales
    path('sales/', views.sales_list, name='sales_list'),  # Access sales at root of the sales section

    # Create a new sale
    path('create/', views.create_sale, name='create_sale'),

    # Edit sale
    path('edit/<int:sale_id>/', views.edit_sale, name='edit_sale'),

    # Delete sale
    path('<int:pk>/delete/', views.delete_sale, name='delete_sale'),

    # Fetch products for the sale
    path('get-products/', views.get_products, name='get_products'),

    # Sale detail view, which should display detailed info about a specific sale

    path('details/<int:sale_id>/', views.sales_detail, name='sales_detail'),  # Ensure this is below other paths to avoid conflict

    # Update sale items (e.g., edit products in a sale)
    path('<int:sale_id>/update_items/', views.update_sale_items, name='update_sale_items'),

    path('sales/<int:sale_id>/delete_item/<int:item_id>/', views.delete_sale_item, name='delete_sale_item'),
]
