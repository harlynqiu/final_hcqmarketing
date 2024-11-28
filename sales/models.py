from django.db import models
from django.utils import timezone
from inventory.models import Product  # Assuming Product model is in the 'inventory' app
from inventory.models import Customer



class Customer(models.Model):
    customer_hardware = models.CharField(max_length=100, default='Unknown')  # Provide a default value
    name = models.CharField(max_length=100)
    email = models.EmailField()
    # Other fields

    def __str__(self):
        return self.customer_hardware 

class Sales(models.Model):
    Sales_Status = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    Sales_Payment = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sales_code = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, choices=Sales_Status, default='Pending')
    payment_status = models.CharField(max_length=50, choices=Sales_Payment, default='Unpaid')

    

    def calculate_total_amount(self):
        """Calculate the total sale amount from the items."""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        self.save()

    def update_stock(self):
        """Update product stock when sale is completed."""
        if self.status == 'Completed':
            for item in self.items.all():
                item.product.stock -= item.quantity  # Reduce stock based on sale quantity
                item.product.save()

    def save(self, *args, **kwargs):
        """Override save method to ensure total amount is calculated."""
        self.calculate_total_amount()
        super().save(*args, **kwargs)

class SalesItem(models.Model):
    sale = models.ForeignKey(Sales, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Assuming you have a Product model in the inventory app
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        """Calculates the total price for this sale item."""
        return self.quantity * self.price_per_item

    def __str__(self):
        return f'{self.product.name} - {self.quantity} @ {self.price_per_item}'

class Payment(models.Model):
    Payment_Method = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Gcash', 'Gcash')
    ]

    Payment_Status = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Partial', 'Partial'),
    ]

    sale = models.ForeignKey(Sales, related_name='payments', on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, choices=Payment_Method, default='Cash')
    payment_status = models.CharField(max_length=50, choices=Payment_Status, default='Completed')

    def __str__(self):
        return f'Payment for Sale {self.sale.sales_code} - {self.amount_paid}'

    def update_payment_status(self):
        """Updates the payment status based on total payments."""
        total_paid = sum(payment.amount_paid for payment in self.sale.payments.all())
        if total_paid >= self.sale.total_amount:
            self.sale.payment_status = 'Paid'
        elif total_paid > 0:
            self.sale.payment_status = 'Partial'
        else:
            self.sale.payment_status = 'Unpaid'
        self.sale.save()