# tailor_app/forms.py

from django import forms
from .models import Customer, Order, Measurement, OrderImage, Appointment, Supplier, InventoryItem, OrderMaterial
from django.forms import inlineformset_factory

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['item', 'status', 'due_date', 'notes', 'price', 'amount_paid', 'fabric_details']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['name', 'value']

class OrderImageForm(forms.ModelForm):
    class Meta:
        model = OrderImage
        fields = ['image', 'caption']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['customer', 'title', 'start_time', 'end_time', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone']
        widgets = { # Add some bootstrap classes
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'supplier', 'quantity_in_stock', 'cost_per_unit', 'reorder_level']
    
    def __init__(self, *args, **kwargs):
        # Filter the supplier dropdown to only show suppliers belonging to the current user
        user = kwargs.pop('user', None)
        super(InventoryItemForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['supplier'].queryset = Supplier.objects.filter(tailor=user)


# Create a formset for linking materials to an order
OrderMaterialFormSet = inlineformset_factory(
    Order, 
    OrderMaterial,
    fields=('material', 'quantity_used'),
    extra=1, # Show one extra form by default
    can_delete=True
)

