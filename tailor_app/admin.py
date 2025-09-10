from django.contrib import admin
from .models import Customer, Order, Measurement

# Inline admin for Measurements to show them on the Customer page
class MeasurementInline(admin.TabularInline):
    model = Measurement
    extra = 1 # Number of empty forms to display

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at')
    search_fields = ('name', 'phone')
    inlines = [MeasurementInline] # Add measurements directly in the customer admin page

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'garment_type', 'due_date', 'status', 'price', 'balance_due')
    list_filter = ('status', 'due_date')
    search_fields = ('customer__name', 'garment_type')

# Register your models here.
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Measurement) # Also register Measurement on its own

