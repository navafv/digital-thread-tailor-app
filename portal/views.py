# portal/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from tailor_app.models import Order, Measurement, Appointment
from .forms import AppointmentRequestForm

@login_required
def portal_dashboard(request):
    # Ensure the logged-in user has a customer profile
    if not hasattr(request.user, 'customer_profile'):
        # Handle case where user is not a client (e.g., a tailor is logged in)
        # Redirect them or show an error
        return redirect('tailor_app:dashboard') 

    customer = request.user.customer_profile

    orders = Order.objects.filter(customer=customer).order_by('-created_at')

    confirmed_appointments = Appointment.objects.filter(customer=customer, status='Confirmed').order_by('start_time')
    pending_appointments = Appointment.objects.filter(customer=customer, status='Requested').order_by('start_time')

    context = {
        'customer': customer,
        'orders': orders,
        'pending_orders': orders.filter(status__in=['Pending', 'In Progress']).count(),
        'completed_orders': orders.filter(status='Completed').count(),
        'confirmed_appointments': confirmed_appointments,
        'pending_appointments': pending_appointments,
    }
    return render(request, 'portal/dashboard.html', context)

@login_required
def portal_order_list(request):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('tailor_app:dashboard')
        
    customer = request.user.customer_profile
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'portal/order_list.html', {'orders': orders})

@login_required
def portal_order_detail(request, pk):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('tailor_app:dashboard')
        
    customer = request.user.customer_profile
    order = get_object_or_404(Order, pk=pk, customer=customer)
    return render(request, 'portal/order_detail.html', {'order': order})

@login_required
def portal_profile(request):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('tailor_app:dashboard')
        
    customer = request.user.customer_profile
    measurements = Measurement.objects.filter(customer=customer)
    return render(request, 'portal/profile.html', {'customer': customer, 'measurements': measurements})

@login_required
def request_appointment(request):
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            # Link to the logged-in customer and their tailor
            appointment.customer = request.user.customer_profile
            appointment.tailor = request.user.customer_profile.tailor
            # CRITICAL: Set the status to 'Requested'
            appointment.status = 'Requested'
            appointment.save()
            return redirect('portal:dashboard')
    else:
        form = AppointmentRequestForm()
    
    return render(request, 'portal/request_appointment.html', {'form': form})

