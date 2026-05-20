from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from . import rag_engine

# Путь к файлу конфигурации (создастся автоматически)
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app_config.json')

def load_config():
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
        except:
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
        data = json.loads(request.body)
        user_message = data.get('message', '')
        ai_response = rag_engine.ask_second_brain(user_message)
        return JsonResponse({'status': 'ok', 'reply': ai_response})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_save_settings(request):
    if request.method == "POST":
        new_config = json.loads(request.body)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, ensure_ascii=False, indent=4)
        
        # Сбрасываем память нейросети, чтобы она применила новые настройки
        rag_engine.reset_chat_engine()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)