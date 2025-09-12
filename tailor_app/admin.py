# tailor_app/admin.py

from django.contrib import admin
from .models import Customer, Order, Measurement, OrderImage

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Measurement)
admin.site.register(OrderImage)

