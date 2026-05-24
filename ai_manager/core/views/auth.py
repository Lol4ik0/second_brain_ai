from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    error_message = None
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = "Registration failed. Invalid username or password patterns."
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form, 'error': error_message})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            error_message = "Authentication failed. Invalid username or security credentials."
    else:
        form = AuthenticationForm()
        
    return render(request, 'registration/login.html', {'form': form, 'error': error_message})

def logout_view(request):
    logout(request)
    return redirect('login')