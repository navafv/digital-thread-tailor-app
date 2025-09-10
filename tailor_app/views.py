from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Order, Measurement
from .forms import CustomerForm, OrderForm, MeasurementForm
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

# --- Dashboard View (NEW) ---
def dashboard(request):
    # Key statistics
    total_customers = Customer.objects.count()
    active_orders_count = Order.objects.exclude(status__in=['Completed', 'Cancelled']).count()

    # Upcoming Deadlines (due in the next 7 days)
    seven_days_from_now = timezone.now().date() + timedelta(days=7)
    upcoming_deadlines = Order.objects.exclude(status__in=['Completed', 'Cancelled']).filter(due_date__lte=seven_days_from_now).order_by('due_date')

    # Recently Created Orders
    recent_orders = Order.objects.order_by('-order_date')[:5] # Get the 5 most recent orders

    context = {
        'total_customers': total_customers,
        'active_orders_count': active_orders_count,
        'upcoming_deadlines': upcoming_deadlines,
        'recent_orders': recent_orders,
    }
    return render(request, 'tailor_app/dashboard.html', context)

# --- Customer Views ---
# ... customer_list, customer_detail, add_customer, edit_customer views are unchanged ...
def customer_list(request):
    # Get the search query from the GET request
    query = request.GET.get('q')
    
    if query:
        # Filter customers by name or phone number containing the query
        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        ).order_by('-created_at')
    else:
        # If no query, get all customers
        customers = Customer.objects.order_by('-created_at')
        
    return render(request, 'tailor_app/customer_list.html', {'customers': customers, 'search_query': query})

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    measurements = Measurement.objects.filter(customer=customer)
    return render(request, 'tailor_app/customer_detail.html', {'customer': customer, 'orders': orders, 'measurements': measurements})

def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, 'tailor_app/add_customer.html', {'form': form})

def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'tailor_app/edit_customer.html', {'form': form, 'customer': customer})


# --- Order Views ---
# ... add_order, order_detail, edit_order views are unchanged ...
def add_order(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = OrderForm()
    return render(request, 'tailor_app/add_order.html', {'form': form, 'customer': customer})

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'tailor_app/order_detail.html', {'order': order})

def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
    return render(request, 'tailor_app/edit_order.html', {'form': form, 'order': order})


# --- Measurement Views (NEW) ---
def add_measurement(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.customer = customer
            measurement.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = MeasurementForm()
    return render(request, 'tailor_app/measurement_form.html', {'form': form, 'customer': customer, 'action': 'Add'})

def edit_measurement(request, pk):
    measurement = get_object_or_404(Measurement, pk=pk)
    customer = measurement.customer
    if request.method == 'POST':
        form = MeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = MeasurementForm(instance=measurement)
    return render(request, 'tailor_app/measurement_form.html', {'form': form, 'customer': customer, 'action': 'Edit'})

def delete_measurement(request, pk):
    measurement = get_object_or_404(Measurement, pk=pk)
    customer_pk = measurement.customer.pk
    if request.method == 'POST':
        measurement.delete()
        return redirect('customer_detail', pk=customer_pk)
    return render(request, 'tailor_app/confirm_delete.html', {'object': measurement, 'cancel_url': reverse_lazy('customer_detail', kwargs={'pk': customer_pk})})

