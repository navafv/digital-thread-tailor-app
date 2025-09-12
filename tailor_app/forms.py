from django import forms
from .models import Customer, Order, Measurement, OrderImage

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['garment_type', 'fabric_details', 'due_date', 'status', 'price', 'amount_paid', 'notes']
        widgets = {
            'garment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'fabric_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class OrderImageForm(forms.ModelForm):
    class Meta:
        model = OrderImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
        }

class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['name', 'value']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chest, Waist, Inseam'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 38.5'}),
        }

