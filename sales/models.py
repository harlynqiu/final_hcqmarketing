from django.db import models
from inventory.models import Product  # Direct import of Product model

class Sale(models.Model):
    customer_name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')])

class SaleItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Directly use the imported Product model
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
