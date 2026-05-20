from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
import json
from .models import UserSettings
from . import rag_engine

# HELPER: Get active config for the current logged-in user, or default system configurations if anonymous
def get_user_config(user):
    if user.is_authenticated:
        # User settings are automatically created via Django signals
        return user.settings
    return {
        "display_name": "Guest Traveler",
        "email": "",
        "theme": "cyberpunk",
        "accent_color": "cyan",
        "ai_model": "llama3",
        "temperature": "0.7"
    }

# --- AUTHENTICATION VIEWS ---
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


# --- PROTECTED APP PAGES ---
@login_required(login_url='login')
def home_view(request):
    return render(request, 'home.html', {'active_page': 'home', 'config': get_user_config(request.user)})

@login_required(login_url='login')
def ai_chat_view(request):
    return render(request, 'ai-chat.html', {'active_page': 'ai-chat', 'config': get_user_config(request.user)})

@login_required(login_url='login')
def notes_view(request):
    return render(request, 'notes.html', {'active_page': 'notes', 'config': get_user_config(request.user)})

@login_required(login_url='login')
def tasks_view(request):
    return render(request, 'tasks.html', {'active_page': 'tasks', 'config': get_user_config(request.user)})

@login_required(login_url='login')
def settings_view(request):
    return render(request, 'settings.html', {'active_page': 'settings', 'config': get_user_config(request.user)})


# --- ASYNC DATABASE API ---
@csrf_exempt
@login_required(login_url='login')
def api_chat_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get('message', '')
        ai_response = rag_engine.ask_second_brain(user_message)
        return JsonResponse({'status': 'ok', 'reply': ai_response})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required(login_url='login')
def api_save_settings(request):
    if request.method == "POST":
        data = json.loads(request.body)
        settings = request.user.settings
        
        # Save into the SQLite Database directly
        settings.display_name = data.get('display_name', settings.display_name)
        settings.theme = data.get('theme', settings.theme)
        settings.accent_color = data.get('accent_color', settings.accent_color)
        settings.ai_model = data.get('ai_model', settings.ai_model)
        settings.temperature = float(data.get('temperature', settings.temperature))
        settings.save()
        
        # Reset current cache engine parameters
        rag_engine.reset_chat_engine()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)