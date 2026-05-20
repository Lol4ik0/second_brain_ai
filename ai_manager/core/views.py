from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from . import rag_engine

# ИСПРАВЛЕНО: Жестко задаем пути, чтобы избежать NameError
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, 'app_config.json')

def load_config():
    """Загружает настройки из файла"""
    defaults = {
        "display_name": "Alex Chen",
        "email": "alex@example.com",
        "theme": "cyberpunk",
        "ai_model": "llama3",
        "temperature": "0.7"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return {**defaults, **json.load(f)}
        except Exception:
            pass
    return defaults

# --- ОТОБРАЖЕНИЕ СТРАНИЦ ---
def home_view(request):
    return render(request, 'home.html', {'active_page': 'home', 'config': load_config()})

def ai_chat_view(request):
    return render(request, 'ai-chat.html', {'active_page': 'ai-chat', 'config': load_config()})

def notes_view(request):
    return render(request, 'notes.html', {'active_page': 'notes', 'config': load_config()})

def tasks_view(request):
    return render(request, 'tasks.html', {'active_page': 'tasks', 'config': load_config()})

def settings_view(request):
    return render(request, 'settings.html', {'active_page': 'settings', 'config': load_config()})

# --- API ---
@csrf_exempt
def api_chat_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            ai_response = rag_engine.ask_second_brain(user_message)
            return JsonResponse({'status': 'ok', 'reply': ai_response})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_save_settings(request):
    if request.method == "POST":
        try:
            new_config = json.loads(request.body)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=4)
            
            # Сбрасываем память нейросети
            rag_engine.reset_chat_engine()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)