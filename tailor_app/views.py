from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Order, Measurement, OrderImage
from .forms import CustomerForm, OrderForm, MeasurementForm, OrderImageForm
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Sum, F
from django.contrib.auth.decorators import login_required

# --- Dashboard ---
@login_required
def dashboard(request):
    # Filter all queries by the logged-in user (the tailor)
    total_customers = Customer.objects.filter(tailor=request.user).count()
    active_orders = Order.objects.filter(customer__tailor=request.user).exclude(status__in=['Completed', 'Cancelled'])
    active_orders_count = active_orders.count()
    outstanding_revenue = active_orders.aggregate(total=Sum(F('price') - F('amount_paid')))['total'] or 0.00
    seven_days_from_now = timezone.now().date() + timedelta(days=7)
    upcoming_deadlines = active_orders.filter(due_date__lte=seven_days_from_now).order_by('due_date')
    recent_orders = Order.objects.filter(customer__tailor=request.user).order_by('-order_date')[:5]

    context = {
        'total_customers': total_customers,
        'active_orders_count': active_orders_count,
        'outstanding_revenue': outstanding_revenue,
        'upcoming_deadlines': upcoming_deadlines,
        'recent_orders': recent_orders,
    }
    return render(request, 'tailor_app/dashboard.html', context)

# --- Customer Views ---
@login_required
def customer_list(request):
    query = request.GET.get('q')
    # Base queryset for the logged-in user
    customers = Customer.objects.filter(tailor=request.user)
    if query:
        customers = customers.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        )
    return render(request, 'tailor_app/customer_list.html', {'customers': customers.order_by('name'), 'query': query})

@login_required
def customer_detail(request, pk):
    # Ensure the customer belongs to the logged-in user
    customer = get_object_or_404(Customer, pk=pk, tailor=request.user)
    return render(request, 'tailor_app/customer_detail.html', {'customer': customer})

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.tailor = request.user # Assign the current user as the tailor
            customer.save()
            return redirect('customer_detail', pk=customer.pk)
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
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'tailor_app/edit_customer.html', {'form': form})

# --- Order Views ---
@login_required
def add_order(request, customer_pk):
    # Ensure the customer belongs to the logged-in user before adding an order
    customer = get_object_or_404(Customer, pk=customer_pk, tailor=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.save()
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'tailor_app/add_order.html', {'form': form, 'customer': customer})

@login_required
def order_detail(request, pk):
    # Ensure the order belongs to a customer of the logged-in user
    order = get_object_or_404(Order, pk=pk, customer__tailor=request.user)
    image_form = OrderImageForm()
    if request.method == 'POST':
        form = OrderImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.order = order
            image_instance.save()
            return redirect('order_detail', pk=order.pk)
    context = {'order': order, 'image_form': image_form}
    return render(request, 'tailor_app/order_detail.html', context)

@login_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk, customer__tailor=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
    return render(request, 'tailor_app/edit_order.html', {'form': form})

@login_required
def delete_order_image(request, pk):
    # Ensure the image belongs to an order of the logged-in user
    image = get_object_or_404(OrderImage, pk=pk, order__customer__tailor=request.user)
    order_pk = image.order.pk
    if request.method == 'POST':
        image.image.delete()
        image.delete()
    return redirect('order_detail', pk=order_pk)

# --- Measurement Views ---
@login_required
def add_measurement(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk, tailor=request.user)
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.customer = customer
            measurement.save()
            return redirect('customer_detail', pk=customer.pk)
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
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = MeasurementForm(instance=measurement)
    return render(request, 'tailor_app/measurement_form.html', {'form': form, 'customer': customer})

@login_required
def delete_measurement(request, pk):
    measurement = get_object_or_404(Measurement, pk=pk, customer__tailor=request.user)
    customer_pk = measurement.customer.pk
    if request.method == 'POST':
        measurement.delete()
        return redirect('customer_detail', pk=customer_pk)
    return render(request, 'tailor_app/confirm_delete.html', {'object': measurement})

