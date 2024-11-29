from django.db import models
from django.utils import timezone
from inventory.models import Product, Customer


class Sales(models.Model):
    SALES_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='sales'
    )
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sales_code = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=50, choices=SALES_STATUS_CHOICES, default='Pending'
    )
    payment_stat = models.CharField(
        max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Unpaid'
    )

    def calculate_total_amount(self):
        """Calculate the total sale amount from the items."""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total

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
        """Override save method to ensure total amount is calculated."""
        self.calculate_total_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale {self.sales_code} - {self.customer.name}"


class SalesItem(models.Model):
    sale = models.ForeignKey(Sales, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        """Calculate the total price for this sale item."""
        return self.quantity * self.price_per_item

    def __str__(self):
        return f"{self.product.name} - {self.quantity} @ {self.price_per_item}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Gcash', 'Gcash'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Partial', 'Partial'),
    ]

    sale = models.ForeignKey(Sales, related_name='payments', on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, default='Cash'
    )
    payment_status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Completed'
    )

    def __str__(self):
        return f"Payment for Sale {self.sale.sales_code} - {self.amount_paid}"

    def update_payment_status(self):
        """Update the payment status of the related sale."""
        total_paid = sum(payment.amount_paid for payment in self.sale.payments.all())
        if total_paid >= self.sale.total_amount:
            self.sale.payment_stat = 'Paid'
        elif total_paid > 0:
            self.sale.payment_stat = 'Partial'
        else:
            self.sale.payment_stat = 'Unpaid'
        self.sale.save()
