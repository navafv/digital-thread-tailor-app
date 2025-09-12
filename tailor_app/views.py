# tailor_app/views.py

import calendar
from datetime import timedelta, date
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.db.models import Sum, F, Q
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.models import User
from django.contrib import messages
import random
import string

from .models import (
    Customer, Order, Measurement, Appointment, 
    Supplier, InventoryItem, WorkflowTemplate, OrderTask
)
from .forms import (
    CustomerForm, OrderForm, MeasurementForm, OrderImageForm, 
    AppointmentForm, SupplierForm, InventoryItemForm, OrderMaterialFormSet,
    WorkflowTemplateForm, TaskDefinitionFormSet, ApplyWorkflowForm
)

@login_required
def dashboard(request):
    customers = Customer.objects.filter(tailor=request.user)
    orders = Order.objects.filter(customer__tailor=request.user)
    
    total_customers = customers.count()
    pending_orders_count = orders.filter(status='Pending').count()
    completed_orders_this_month = orders.filter(
        status='Completed',
        updated_at__year=timezone.now().year,
        updated_at__month=timezone.now().month
    ).count()

    outstanding_revenue = orders.exclude(status__in=['Completed', 'Cancelled']).aggregate(
        total_balance=Sum(F('price') - F('amount_paid'))
    )['total_balance'] or 0.00

    pending_requests = Appointment.objects.filter(
        tailor=request.user, 
        status='Requested'
    ).order_by('start_time')

    low_stock_items = InventoryItem.objects.filter(
        tailor=request.user,
        quantity_in_stock__lte=models.F('reorder_level')
    ).order_by('quantity_in_stock')
    
    # --- ROBUST 6-MONTH CHART LOGIC ---
    revenue_data_list = []
    today = date.today()
    for i in range(6):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1

        monthly_revenue = orders.filter(
            status='Completed',
            updated_at__year=year,
            updated_at__month=month
        ).aggregate(total_revenue=Sum('price'))['total_revenue'] or 0

        month_name = date(year, month, 1).strftime('%B')
        revenue_data_list.append({'month': month_name, 'revenue': float(monthly_revenue)})

    revenue_data_list.reverse()
    revenue_data_keys = [item['month'] for item in revenue_data_list]
    revenue_data_values = [item['revenue'] for item in revenue_data_list]

    context = {
        'total_customers': total_customers,
        'pending_orders': pending_orders_count,
        'completed_orders_this_month': completed_orders_this_month,
        'outstanding_revenue': outstanding_revenue,
        'pending_requests': pending_requests,
        'low_stock_items': low_stock_items,
        'revenue_data_keys': revenue_data_keys,
        'revenue_data_values': revenue_data_values,
    }
    return render(request, 'tailor_app/dashboard.html', context)


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
            Q(name__icontains=query) | Q(phone__icontains=query),
            tailor=request.user
        )
    else:
        customers = Customer.objects.filter(tailor=request.user).order_by('name')
    return render(request, 'tailor_app/customer_list.html', {'customers': customers})

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id, tailor=request.user)
    return render(request, 'tailor_app/customer_detail.html', {'customer': customer})

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.tailor = request.user
            customer.save()
            return redirect('tailor_app:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm()
    return render(request, 'tailor_app/add_customer.html', {'form': form})

@login_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id, tailor=request.user)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('tailor_app:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'tailor_app/edit_customer.html', {'form': form, 'customer': customer})

@login_required
def add_order(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id, tailor=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.save()
            return redirect('tailor_app:order_detail', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'tailor_app/add_order.html', {'form': form, 'customer': customer})

@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer__tailor=request.user)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        material_formset = OrderMaterialFormSet(request.POST, instance=order, prefix='materials')
        
        if form.is_valid() and material_formset.is_valid():
            form.save()
            material_formset.save()
            return redirect('tailor_app:order_detail', order_id=order.id)
    else:
        form = OrderForm(instance=order)
        material_formset = OrderMaterialFormSet(instance=order, prefix='materials')
        
    context = {
        'form': form,
        'material_formset': material_formset,
        'order': order
    }
    return render(request, 'tailor_app/edit_order.html', context)

@login_required
def add_measurement(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id, tailor=request.user)
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.customer = customer
            measurement.save()
    return redirect('tailor_app:customer_detail', customer_id=customer_id)

@login_required
def edit_measurement(request, measurement_id):
    measurement = get_object_or_404(Measurement, pk=measurement_id, customer__tailor=request.user)
    if request.method == 'POST':
        form = MeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            return redirect('tailor_app:customer_detail', customer_id=measurement.customer.id)
    else:
        form = MeasurementForm(instance=measurement)
    return render(request, 'tailor_app/measurement_form.html', {'form': form, 'measurement': measurement})

@login_required
def delete_measurement(request, measurement_id):
    measurement = get_object_or_404(Measurement, pk=measurement_id, customer__tailor=request.user)
    if request.method == 'POST':
        measurement.delete()
        return redirect('tailor_app:customer_detail', customer_id=measurement.customer.id)
    return render(request, 'tailor_app/confirm_delete.html', {'object': measurement})

@login_required
def generate_pdf_invoice(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer__tailor=request.user)
    html_string = render_to_string('tailor_app/invoice_template.html', {'order': order})
    
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    return response

@login_required
def invite_customer_to_portal(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id, tailor=request.user)
    if not customer.client_account:
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        base_username = f"{customer.name.split(' ')[0].lower()}{customer.id}"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(username=username, password=temp_password, email=customer.email)
        customer.client_account = user
        customer.save()
        messages.success(request, f"Client account created. Username: '{username}', Temp Pass: '{temp_password}'.")
    else:
        messages.info(request, "This customer already has a client portal account.")
    return redirect('tailor_app:customer_detail', customer_id=customer.id)

@login_required
def calendar_view(request):
    form = AppointmentForm(user=request.user)
    return render(request, 'tailor_app/calendar.html', {'form': form})

@login_required
def calendar_events_api(request):
    orders = Order.objects.filter(customer__tailor=request.user)
    order_events = [
        {'title': f"Due: {order.item}", 'start': order.due_date.isoformat(), 'allDay': True, 'backgroundColor': '#dc3545', 'borderColor': '#dc3545', 'url': reverse('tailor_app:order_detail', args=[order.id])}
        for order in orders
    ]
    appointments = Appointment.objects.filter(tailor=request.user)
    appointment_events = [
        {'title': appt.title, 'start': appt.start_time.isoformat(), 'end': appt.end_time.isoformat(), 'backgroundColor': '#ffc107' if appt.status == 'Requested' else '#0d6efd', 'borderColor': '#ffc107' if appt.status == 'Requested' else '#0d6efd', 'extendedProps': { 'notes': appt.notes }}
        for appt in appointments
    ]
    events = order_events + appointment_events
    return JsonResponse(events, safe=False)

@login_required
def add_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.tailor = request.user
            appointment.status = 'Confirmed'
            appointment.save()
    return redirect('tailor_app:calendar')

@login_required
def update_appointment_status(request, appointment_id, new_status):
    appointment = get_object_or_404(Appointment, pk=appointment_id, tailor=request.user)
    if new_status in ['Confirmed', 'Cancelled']:
        appointment.status = new_status
        appointment.save()
        messages.success(request, f"Appointment request has been {new_status.lower()}.")
    return redirect('tailor_app:dashboard')

# ----- Inventory & Supplier Views -----
@login_required
def inventory_list(request):
    items = InventoryItem.objects.filter(tailor=request.user).order_by('name')
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

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.filter(tailor=request.user).order_by('name')
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

# --- WORKFLOW & TASK VIEWS ---
@login_required
def workflow_template_list(request):
    templates = WorkflowTemplate.objects.filter(tailor=request.user)
    return render(request, 'tailor_app/workflow_template_list.html', {'templates': templates})

@login_required
def create_workflow_template(request):
    if request.method == 'POST':
        form = WorkflowTemplateForm(request.POST)
        template = WorkflowTemplate(tailor=request.user) # Create instance but don't save yet
        formset = TaskDefinitionFormSet(request.POST, instance=template)
        if form.is_valid() and formset.is_valid():
            template = form.save(commit=False)
            template.tailor = request.user
            template.save()
            formset.instance = template
            formset.save()
            messages.success(request, "Workflow template created successfully.")
            return redirect('tailor_app:workflow_list')
    else:
        form = WorkflowTemplateForm()
        formset = TaskDefinitionFormSet()
    return render(request, 'tailor_app/workflow_template_form.html', {'form': form, 'formset': formset})

@login_required
def edit_workflow_template(request, template_id):
    template = get_object_or_404(WorkflowTemplate, pk=template_id, tailor=request.user)
    if request.method == 'POST':
        form = WorkflowTemplateForm(request.POST, instance=template)
        formset = TaskDefinitionFormSet(request.POST, instance=template)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Workflow template updated successfully.")
            return redirect('tailor_app:workflow_list')
    else:
        form = WorkflowTemplateForm(instance=template)
        formset = TaskDefinitionFormSet(instance=template)
    return render(request, 'tailor_app/workflow_template_form.html', {'form': form, 'formset': formset, 'template': template})

@login_required
def apply_workflow_to_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer__tailor=request.user)
    if request.method == 'POST':
        form = ApplyWorkflowForm(request.POST, user=request.user)
        if form.is_valid():
            template = form.cleaned_data['template']
            for task_def in template.tasks.all():
                OrderTask.objects.create(order=order, task_definition=task_def)
            messages.success(request, f"Workflow '{template.name}' applied to the order.")
    return redirect('tailor_app:order_detail', order_id=order.id)

@login_required
def update_order_task_status(request, task_id):
    task = get_object_or_404(OrderTask, pk=task_id, order__customer__tailor=request.user)
    if request.method == 'POST':
        is_completed = request.POST.get('is_completed') == 'on'
        task.is_completed = is_completed
        task.completed_at = timezone.now() if is_completed else None
        task.save()
    return redirect('tailor_app:order_detail', order_id=task.order.id)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer__tailor=request.user)
    image_form = OrderImageForm()
    
    if request.method == 'POST':
        # This handles the image upload form submission
        image_form = OrderImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            order_image = image_form.save(commit=False)
            order_image.order = order
            order_image.save()
            messages.success(request, "Image uploaded successfully.")
            return redirect('tailor_app:order_detail', order_id=order.id)

    apply_workflow_form = ApplyWorkflowForm(user=request.user)
    
    context = {
        'order': order,
        'image_form': image_form,
        'apply_workflow_form': apply_workflow_form,
    }
    return render(request, 'tailor_app/order_detail.html', context)

