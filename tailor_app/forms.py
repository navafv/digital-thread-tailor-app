# tailor_app/forms.py

from django import forms
from .models import (
    Customer, Order, Measurement, OrderImage, 
    Appointment, Supplier, InventoryItem, OrderMaterial,
    WorkflowTemplate, TaskDefinition
)
from django.forms import inlineformset_factory

# This is the base class that will add the 'form-control' class to all fields
class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # Add form-control class to all fields
            field.widget.attrs.setdefault('class', 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input')

class CustomerForm(BootstrapModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']

class OrderForm(BootstrapModelForm):
    class Meta:
        model = Order
        fields = ['item', 'status', 'due_date', 'notes', 'price', 'amount_paid', 'fabric_details']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class MeasurementForm(BootstrapModelForm):
    class Meta:
        model = Measurement
        fields = ['name', 'value']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'
            }),
            'value': forms.TextInput(attrs={
                'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'
            }),
        }

class OrderImageForm(BootstrapModelForm):
    class Meta:
        model = OrderImage
        fields = ['image', 'caption']

class AppointmentForm(BootstrapModelForm):
    class Meta:
        model = Appointment
        fields = ['customer', 'title', 'start_time', 'end_time', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['customer'].queryset = Customer.objects.filter(tailor=user)

class SupplierForm(BootstrapModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone']

class InventoryItemForm(BootstrapModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'supplier', 'quantity_in_stock', 'cost_per_unit', 'reorder_level']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['supplier'].queryset = Supplier.objects.filter(tailor=user)

OrderMaterialFormSet = inlineformset_factory(
    Order, 
    OrderMaterial,
    fields=('material', 'quantity_used'),
    extra=1,
    can_delete=True,
    widgets = {
        'material': forms.Select(attrs={'class': 'block w-full mt-1 text-sm dark:text-gray-300 dark:border-gray-600 dark:bg-gray-700 form-select focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:focus:shadow-outline-gray'}),
        'quantity_used': forms.NumberInput(attrs={'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'}),
    }
)

class WorkflowTemplateForm(BootstrapModelForm):
    class Meta:
        model = WorkflowTemplate
        fields = ['name']

# --- THIS IS THE CORRECTED FORMSET ---
TaskDefinitionFormSet = inlineformset_factory(
    WorkflowTemplate,
    TaskDefinition,
    # 'DELETE' has been removed from the fields list
    fields=('name', 'order'), 
    extra=1,
    can_delete=True,
    widgets = {
        'name': forms.TextInput(attrs={'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'}),
        'order': forms.NumberInput(attrs={'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'}),
    }
)
# --- END OF CORRECTION ---

class ApplyWorkflowForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=WorkflowTemplate.objects.none(),
        label="Select a Workflow Template",
        empty_label="--- Choose a Template ---",
        widget=forms.Select(attrs={'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['template'].queryset = WorkflowTemplate.objects.filter(tailor=user)

