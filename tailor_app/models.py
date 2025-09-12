from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # Import the User model

class Customer(models.Model):
    tailor = models.ForeignKey(User, on_delete=models.CASCADE) # Link to the tailor (user)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        # A tailor cannot have two customers with the same phone number
        unique_together = ('tailor', 'phone',)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Measuring', 'Measuring'),
        ('Cutting', 'Cutting'),
        ('Stitching', 'Stitching'),
        ('Fitting', 'Fitting'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    garment_type = models.CharField(max_length=100)
    fabric_details = models.TextField()
    order_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    notes = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def balance_due(self):
        return self.price - self.amount_paid

    def __str__(self):
        return f"{self.garment_type} for {self.customer.name}"

class OrderImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='order_images/')
    caption = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for order {self.order.id}"

class Measurement(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='measurements')
    name = models.CharField(max_length=50) # e.g., Chest, Waist, Inseam
    value = models.DecimalField(max_digits=5, decimal_places=2) # e.g., 38.5 inches
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.value} for {self.customer.name}"

