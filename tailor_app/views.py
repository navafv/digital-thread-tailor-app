# tailor_app/views.py

import calendar
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.template.loader import get_template
from weasyprint import HTML
from django.contrib.auth.models import User
from django.contrib import messages
import random
import string

from .models import Customer, Order, Measurement, OrderImage, Appointment, Supplier, InventoryItem
from .forms import CustomerForm, OrderForm, MeasurementForm, OrderImageForm, AppointmentForm, SupplierForm, InventoryItemForm, OrderMaterialFormSet

@login_required
def dashboard(request):
    customers = Customer.objects.filter(tailor=request.user)
    orders = Order.objects.filter(customer__tailor=request.user)
    
    total_customers = customers.count()
    pending_orders = orders.filter(status='Pending').count()
    completed_orders_this_month = orders.filter(
        status='Completed',
        updated_at__month=timezone.now().month
    ).count()

    outstanding_revenue = orders.exclude(status__in=['Completed', 'Delivered', 'Cancelled']).aggregate(
        total_balance=Sum('price') - Sum('amount_paid')
    )['total_balance'] or 0.00

    pending_requests = Appointment.objects.filter(
        tailor=request.user, 
        status='Requested'
    ).order_by('start_time')

    low_stock_items = InventoryItem.objects.filter(
        tailor=request.user,
        quantity_in_stock__lte=models.F('reorder_level') # F() allows comparing two fields
    ).order_by('quantity_in_stock')

    context = {
        'total_customers': total_customers,
        'pending_orders': pending_orders,
        'completed_orders_this_month': completed_orders_this_month,
        'outstanding_revenue': outstanding_revenue,
        'pending_requests': pending_requests,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'tailor_app/dashboard.html', context)

@login_required
def get_monthly_revenue_data(request):
    six_months_ago = timezone.now() - timedelta(days=180)
    revenue_data = Order.objects.filter(
        customer__tailor=request.user,
        status__in=['Completed', 'Delivered'],
        updated_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('updated_at')
    ).values('month').annotate(
        total_revenue=Sum('price')
    ).order_by('month')

    data = {
        "labels": [calendar.month_name[item['month'].month] for item in revenue_data],
        "values": [float(item['total_revenue']) for item in revenue_data],
    }
    return JsonResponse(data)

@login_required
def reports_view(request):
    orders = Order.objects.filter(customer__tailor=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'tailor_app/reports.html', context)

@login_required
def customer_list(request):
    query = request.GET.get('q')
    if query:
        customers = Customer.objects.filter(
            models.Q(name__icontains=query) | models.Q(phone__icontains=query),
            tailor=request.user
        )
    else:
        customers = Customer.objects.filter(tailor=request.user)
    return render(request, 'tailor_app/customer_list.html', {'customers': customers})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk, tailor=request.user)
    return render(request, 'tailor_app/customer_detail.html', {'customer': customer})

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.tailor = request.user
            customer.save()
            return redirect('tailor_app:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, 'tailor_app/add_customer.html', {'form': form})

@login_required
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk, tailor=request.user)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('tailor_app:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'tailor_app/edit_customer.html', {'form': form, 'customer': customer})

@login_required
def add_order(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk, tailor=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.save()
            return redirect('tailor_app:order_detail', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'tailor_app/add_order.html', {'form': form, 'customer': customer})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, customer__tailor=request.user)
    image_form = OrderImageForm()
    if request.method == 'POST':
        image_form = OrderImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            order_image = image_form.save(commit=False)
            order_image.order = order
            order_image.save()
            return redirect('tailor_app:order_detail', pk=order.pk)
            
    return render(request, 'tailor_app/order_detail.html', {'order': order, 'image_form': image_form})

@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer__tailor=request.user)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        material_formset = OrderMaterialFormSet(request.POST, instance=order)
        
        if form.is_valid() and material_formset.is_valid():
            # ... stock deduction logic can be added here
            form.save()
            material_formset.save()
            return redirect('tailor_app:order_detail', order_id=order.id)
    else:
        form = OrderForm(instance=order)
        material_formset = OrderMaterialFormSet(instance=order)
        
    context = {
        'form': form,
        'material_formset': material_formset, # Add formset to context
        'order': order
    }
    return render(request, 'tailor_app/edit_order.html', context)

@login_required
def add_measurement(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk, tailor=request.user)
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.customer = customer
            measurement.save()
            return redirect('tailor_app:customer_detail', pk=customer.pk)
    else:
        form = MeasurementForm()
    return render(request, 'tailor_app/measurement_form.html', {'form': form, 'customer': customer})

@login_required
def edit_measurement(request, pk):
    measurement = get_object_or_404(Measurement, pk=pk, customer__tailor=request.user)
    customer = measurement.customer
    if request.method == 'POST':
        form = MeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            return redirect('tailor_app:customer_detail', pk=customer.pk)
    else:
        form = MeasurementForm(instance=measurement)
    return render(request, 'tailor_app/measurement_form.html', {'form': form, 'customer': customer})

@login_required
def delete_measurement(request, pk):
    measurement = get_object_or_404(Measurement, pk=pk, customer__tailor=request.user)
    customer_pk = measurement.customer.pk
    if request.method == 'POST':
        measurement.delete()
        return redirect('tailor_app:customer_detail', pk=customer_pk)
    return render(request, 'tailor_app/confirm_delete.html', {'object': measurement})

@login_required
def generate_pdf_invoice(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, customer__tailor=request.user)
    template = get_template('tailor_app/invoice_template.html')
    html = template.render({'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    
    HTML(string=html).write_pdf(response)
    
    return response

@login_required
def invite_customer_to_portal(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk, tailor=request.user)
    if not customer.client_account:
        # Generate a secure temporary password
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Create a username (ensure it's unique)
        base_username = f"{customer.name.split(' ')[0].lower()}{customer.pk}"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create the user account
        user = User.objects.create_user(username=username, password=temp_password, email=customer.email)
        
        # Link the new user account to the customer profile
        customer.client_account = user
        customer.save()

        # Display the temporary credentials to the tailor
        messages.success(request, f"Client account created for {customer.name}. Username: '{username}', Temporary Password: '{temp_password}'. Please share these credentials securely with your client.")
    else:
        messages.info(request, "This customer already has a client portal account.")
        
    return redirect('tailor_app:customer_detail', pk=customer.pk)

@login_required
def calendar_view(request):
    form = AppointmentForm()
    # We can pre-fill the customer dropdown for the tailor
    form.fields['customer'].queryset = Customer.objects.filter(tailor=request.user)
    return render(request, 'tailor_app/calendar.html', {'form': form})

@login_required
def calendar_events_api(request):
    # Fetch order due dates
    orders = Order.objects.filter(customer__tailor=request.user)
    order_events = [
        {
            'title': f"Due: {order.item}",
            'start': order.due_date.isoformat(),
            'allDay': True,
            'backgroundColor': '#dc3545', # Red for deadlines
            'borderColor': '#dc3545',
            'url': reverse('tailor_app:order_detail', args=[order.pk])
        } for order in orders
    ]
    
    # Fetch appointments
    appointments = Appointment.objects.filter(tailor=request.user)
    appointment_events = []
    for appointment in appointments:
        # Set color based on status
        if appointment.status == 'Confirmed':
            color = '#0d6efd' # Blue
        elif appointment.status == 'Requested':
            color = '#ffc107' # Yellow
        else:
            color = '#6c757d' # Grey for cancelled/completed
            
        appointment_events.append({
            'title': appointment.title,
            'start': appointment.start_time.isoformat(),
            'end': appointment.end_time.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': { 'notes': appointment.notes }
        })
    
    events = order_events + appointment_events
    return JsonResponse(events, safe=False)

@login_required
def add_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.tailor = request.user
            appointment.save()
            return redirect('tailor_app:calendar')
    # If form is not valid or method is not POST, redirect to calendar
    return redirect('tailor_app:calendar')

@login_required
def update_appointment_status(request, appointment_id, new_status):
    appointment = get_object_or_404(Appointment, pk=appointment_id, tailor=request.user)
    if new_status in ['Confirmed', 'Cancelled']: # Add any other statuses you want to allow
        appointment.status = new_status
        appointment.save()
    return redirect('tailor_app:dashboard')

# ----- Inventory Views -----
@login_required
def inventory_list(request):
    items = InventoryItem.objects.filter(tailor=request.user)
    return render(request, 'tailor_app/inventory_list.html', {'items': items})

@login_required
def add_inventory_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.tailor = request.user
            item.save()
            return redirect('tailor_app:inventory_list')
    else:
        form = InventoryItemForm(user=request.user)
    return render(request, 'tailor_app/inventory_form.html', {'form': form})

@login_required
def edit_inventory_item(request, item_id):
    item = get_object_or_404(InventoryItem, pk=item_id, tailor=request.user)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('tailor_app:inventory_list')
    else:
        form = InventoryItemForm(instance=item, user=request.user)
    return render(request, 'tailor_app/inventory_form.html', {'form': form, 'item': item})

# ----- Supplier Views -----
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.filter(tailor=request.user)
    return render(request, 'tailor_app/supplier_list.html', {'suppliers': suppliers})

@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.tailor = request.user
            supplier.save()
            return redirect('tailor_app:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'tailor_app/supplier_form.html', {'form': form})

@login_required
def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id, tailor=request.user)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('tailor_app:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'tailor_app/supplier_form.html', {'form': form, 'supplier': supplier})

