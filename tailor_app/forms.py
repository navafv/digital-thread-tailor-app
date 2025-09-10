from django import forms
from .models import Customer, Order, Measurement

# ... CustomerForm and OrderForm remain the same ...
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email (optional)'}),
        }

# Form for creating new orders
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # We don't include 'customer' here because it will be set in the view
        fields = ['garment_type', 'fabric_details', 'style_notes', 'due_date', 'price', 'amount_paid', 'status']
        widgets = {
            'garment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'fabric_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'style_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


# Form for adding/editing measurements (NEW)
class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['measurement_name', 'value']
        widgets = {
            'measurement_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chest'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Inches'}),
        }

