from django.db import models
from products.models import Product  # Import the Product model from the product app
from customers.models import Customer 

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')  # 'Product' will have a reverse relationship to 'Inventory'
    customer_hardware = models.ForeignKey(Customer, on_delete=models.SET_DEFAULT, default=1)  # Use a default customer ID for inventory if none provided
    inventory_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Inventory for {self.product.product_name} - {self.customer_hardware.customer_hardware}"  # Use customer hardware name in string representation


class StockHistory(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="stock_history")  # Related to the Inventory
    purchase = models.ForeignKey('purchases.Purchase', on_delete=models.CASCADE, related_name='stock_history')  # Reference to a Purchase
    status = models.CharField(max_length=50)  # E.g., "Delivered", "Partially Delivered", etc.
    delivered_quantity = models.PositiveIntegerField()
    remarks = models.TextField(blank=True, null=True)  # Optional remarks
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inventory.product.product_name} - {self.status} ({self.delivered_quantity})"
