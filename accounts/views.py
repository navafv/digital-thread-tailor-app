# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # A new user signing up is always a tailor for now
            return redirect('tailor_app:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # --- THIS IS THE NEW LOGIC ---
            # We check if the logged-in user has a 'customer_profile'.
            # This profile is only created for clients.
            if hasattr(user, 'customer_profile'):
                # If they do, they are a client. Send them to the client portal.
                return redirect('portal:dashboard')
            else:
                # If they don't, they are a tailor. Send them to the main dashboard.
                return redirect('tailor_app:dashboard')
            # --- END OF NEW LOGIC ---

    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

