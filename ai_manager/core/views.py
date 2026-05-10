from django.shortcuts import render
from django.http import JsonResponse
import json
from . import rag_engine

# --- ОТОБРАЖЕНИЕ СТРАНИЦ ---

def home_view(request):
    """Отдает главную страницу (home.html)"""
    return render(request, 'home.html')

def ai_chat_view(request):
    """Отдает страницу чата (ai-chat.html)"""
    return render(request, 'ai-chat.html')

def notes_view(request):
    """Отдает страницу заметок (notes.html)"""
    return render(request, 'notes.html')

def tasks_view(request):
    """Отдает страницу задач (tasks.html)"""
    return render(request, 'tasks.html')

def settings_view(request):
    """Отдает страницу настроек (settings.html)"""
    return render(request, 'settings.html')

# --- API ДЛЯ ОБЩЕНИЯ С ИИ ---

def api_chat_message(request):
    """
    Принимает POST-запрос с текстом от пользователя, 
    передает его в rag_engine и возвращает ответ ИИ.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # Обращаемся к нашему скрипту LlamaIndex
        ai_response = rag_engine.ask_second_brain(user_message)
        
        # Возвращаем JSON ответ обратно в браузер
        return JsonResponse({'status': 'ok', 'reply': ai_response})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)