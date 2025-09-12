# tailor_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Supplier(models.Model):
    tailor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    tailor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.PositiveIntegerField(default=10, help_text="Quantity at which to reorder")

    def __str__(self):
        return self.name

class Customer(models.Model):
    client_account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_profile')
    tailor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    item = models.CharField(max_length=255)
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    due_date = models.DateField()
    
    # ADDING THESE TWO FIELDS BACK
    notes = models.TextField(blank=True, null=True)
    fabric_details = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    materials = models.ManyToManyField(InventoryItem, through='OrderMaterial')

    @property
    def balance_due(self):
        return self.price - self.amount_paid

    def __str__(self):
        return f"Order for {self.item} for {self.customer.name}"

class Measurement(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='measurements')
    name = models.CharField(max_length=50)  # e.g., Chest, Waist, Inseam
    value = models.DecimalField(max_digits=5, decimal_places=2) # e.g., 38.50 (inches or cm)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.value} for {self.customer.name}"

class OrderImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='order_images/')
    caption = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Order #{self.order.id}"

class Appointment(models.Model):
    # Updated STATUS_CHOICES to include 'Requested'
    STATUS_CHOICES = [
        ('Requested', 'Requested'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]
    
    tailor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # The default for appointments created by the tailor is still 'Confirmed'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} for {self.customer.name}"

class OrderMaterial(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    material = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField()

    class Meta:
        unique_together = ('order', 'material')

