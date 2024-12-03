from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [

    path('sales/', views.sales_list, name='sales_list'),
    path('sales/create/', views.create_sale, name='create_sale'),
    path('sales/edit/<int:sale_id>/', views.edit_sale, name='edit_sale'),
    path('<int:pk>/delete/', views.delete_sale, name='delete_sale'),
    path('get-products/', views.get_products, name='get_products'),
    path('<int:sale_id>/', views.sales_detail, name='sales_detail'),
    path('sales/<int:sale_id>/update_items/', views.update_sale_items, name='update_sale_items'),
    path('sales/change_status/<int:sale_id>/', views.change_sale_status, name='change_sale_status'),
    # Optional: URL for deleting a sale (if needed)
    # path('sales/delete/<int:sale_id>/', views.delete_sale, name='delete_sale'),
]