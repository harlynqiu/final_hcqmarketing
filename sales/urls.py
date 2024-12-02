from django.urls import path
from . import views

urlpatterns = [

    path('sales/', views.sales_list, name='sales_list'),
    path('sales/create/', views.create_sale, name='create_sale'),
    path('sales/edit/<int:sale_id>/', views.edit_sale, name='edit_sale'),
    path('<int:pk>/delete/', views.delete_sale, name='delete_sale'),
    path('get-products/', views.get_products, name='get_products'),

    # Optional: URL for deleting a sale (if needed)
    # path('sales/delete/<int:sale_id>/', views.delete_sale, name='delete_sale'),
]