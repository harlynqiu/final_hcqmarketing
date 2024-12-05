from django.db import models
from django.utils import timezone
import random
import string
from inventory.models import Product, Customer
import sales

class Sales(models.Model):
    SALES_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Online', 'Online'),
        ('Terms', 'Terms'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales')
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sales_code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=SALES_STATUS_CHOICES, default='Pending')
    payment_stat = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Cash')
    sales_invoice = models.OneToOneField('Invoice', on_delete=models.SET_NULL, null=True, blank=True)  # Renamed field

    def generate_sales_code(self):
        """Generate a unique sales code in the format SAL-YYYYMMDD-XXXX."""
        today = timezone.now().date()  # Get today's date
        date_str = today.strftime("%Y%m%d")  # Format the date as YYYYMMDD

        # Find the last sale from today and increment its number
        last_sale = Sales.objects.filter(date__date=today).order_by('-id').first()

        # Check if last_sale exists
        if last_sale and last_sale.sales_code:
            # Extract the numeric part of the sales code and increment it
            last_code_number = int(last_sale.sales_code.split('-')[-1])
            new_code_number = last_code_number + 1
        else:
            new_code_number = 1  # Start with 1 if it's the first sale of the day

        # Format the sales code
        return f"SAL-{date_str}-{new_code_number:04d}"  # Ensure the number is zero-padded to 4 digits

    def calculate_total_amount(self):
        """Calculate the total sale amount from the items."""
        if self.pk is not None:  # Ensure calculation only after the sale has a primary key
            total = sum(item.total_price for item in self.items.all())
            return total
        return 0  # Return 0 if no items or if the sale has no primary key

    def update_stock(self):
        """Update product stock when sale is completed."""
        if self.status == 'Completed':
            for item in self.items.all():
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save()
                else:
                    raise ValueError(
                        f"Not enough stock for product: {item.product.name}"
                    )

    def save(self, *args, **kwargs):
        """Override save to avoid recalculating total during save."""
        if not self.sales_code:
            self.sales_code = self.generate_sales_code()

        # Call the original save method first (without total amount calculation)
        super().save(*args, **kwargs)

        # Calculate the total after saving and update the field
        self.total_amount = self.calculate_total_amount()

        # Update only the total_amount field to avoid recursion
        self.update_fields = ['total_amount']
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale {self.sales_code} - {self.customer.name}"


class SalesItem(models.Model):
    sale = models.ForeignKey(Sales, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def total_price(self):
        """Calculate the total price for this sale item."""
        if self.quantity is not None and self.price_per_item is not None:
            return self.quantity * self.price_per_item
        return 0  # Return 0 if either value is None

    def save(self, *args, **kwargs):
        # Automatically set price_per_item from related product's price if it's not set
        if not self.price_per_item:
            self.price_per_item = self.product.product_price
        super().save(*args, **kwargs)

        # Update the total amount in the related sale
        self.sale.calculate_total_amount()
        self.sale.save()

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} @ {self.price_per_item}"


class Invoice(models.Model):
    sale = models.OneToOneField(Sales, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    shipment_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)


class SalesReturn(models.Model):
    return_code = models.CharField(max_length=100)
    sales = models.ForeignKey(Sales, related_name="sales_returns", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateField()

    def __str__(self):
        return f"Return for {self.sales.sales_code} ({self.return_code})"