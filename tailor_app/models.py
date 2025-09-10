from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

# Model for a customer
class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Model for a measurement associated with a customer (NEW)
class Measurement(models.Model):
    customer = models.ForeignKey(Customer, related_name='measurements', on_delete=models.CASCADE)
    measurement_name = models.CharField(max_length=100, help_text="e.g., Chest, Waist, Sleeve Length")
    value = models.DecimalField(max_digits=5, decimal_places=2, help_text="Measurement in inches or cm")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure a customer can only have one of each measurement type
        unique_together = ('customer', 'measurement_name')
        ordering = ['measurement_name']

    def __str__(self):
        return f"{self.customer.name} - {self.measurement_name}: {self.value}"

# Model for an order
class Order(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Stitching', 'Stitching'),
        ('Ready', 'Ready for Pickup'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    garment_type = models.CharField(max_length=100)
    fabric_details = models.TextField(blank=True)
    style_notes = models.TextField(blank=True)
    order_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')

    @property
    def balance_due(self):
        return self.price - self.amount_paid

    def __str__(self):
        return f"Order #{self.id} for {self.customer.name}"

