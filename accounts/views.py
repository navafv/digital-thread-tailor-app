# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
# Import our new custom forms
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def signup_view(request):
    if request.method == 'POST':
        # Use the custom form
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tailor_app:dashboard')
    else:
        # Use the custom form
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        # Use the custom form
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if hasattr(user, 'customer_profile'):
                return redirect('portal:dashboard')
            else:
                return redirect('tailor_app:dashboard')
    else:
        # Use the custom form
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('accounts:login')

