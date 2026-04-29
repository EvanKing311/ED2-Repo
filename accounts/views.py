from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.decorators import login_required

#Handles storing registration info and sending new user to login page
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        user = CustomUser.objects.create_user(username=username, password=password, role=role)
        messages.success(request, "Account created successfully!")
        return redirect('login')
    return render(request, 'register.html')

#Check existing user data and login w/ Django's built-in login
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

#Django built-in logout
@login_required
def logout_view(request):
    #Clear any active control locks for this user when they log out
    from MatlabApp.models import ControlLock
    ControlLock.objects.filter(
        session_key=request.session.session_key
    ).delete()
    
    logout(request)
    return redirect('login')

def demo_login(request):
    from accounts.models import CustomUser
    try:
        demo_user = CustomUser.objects.get(username='showcase', is_viewer=True)
        login(request, demo_user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('experiment_run_dynamic', experiment_name='CartControl')
    except CustomUser.DoesNotExist:
        return redirect('login')