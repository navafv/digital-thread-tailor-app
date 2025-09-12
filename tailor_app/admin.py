from django.contrib import admin
from .models import Customer, Order, Measurement, OrderImage

class OrderImageInline(admin.TabularInline):
    model = OrderImage
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'garment_type', 'due_date', 'status', 'price', 'balance_due')
    list_filter = ('status', 'due_date')
    search_fields = ('customer__name', 'garment_type')
    inlines = [OrderImageInline]

class MeasurementInline(admin.TabularInline):
    model = Measurement
    extra = 1

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone')
    inlines = [MeasurementInline]

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Measurement)
admin.site.register(OrderImage)

