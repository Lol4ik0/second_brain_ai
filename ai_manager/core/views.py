import os
import json
import markdown
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import UserSettings, Task
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
    # Fetch tasks for Kanban board
    tasks = Task.objects.filter(user=request.user)
    context = {
        'active_page': 'home', 
        'config': get_user_config(request.user),
        'todo_tasks': tasks.filter(status='todo'),
        'progress_tasks': tasks.filter(status='in_progress'),
        'done_tasks': tasks.filter(status='done'),
        'recent_tasks': tasks.order_by('-created_at')[:4]
    }
    return render(request, 'home.html', context)

@login_required(login_url='login')
def ai_chat_view(request):
    return render(request, 'ai-chat.html', {'active_page': 'ai-chat', 'config': get_user_config(request.user)})

@login_required(login_url='login')
def notes_view(request):
    from .rag_engine import get_user_paths
    from .git_sync import sync_obsidian_repo
    import os # Make sure os is imported
    
    paths = get_user_paths(request.user)
    settings = request.user.settings
    
    # NEW LOGIC: Check if the hidden '.git' folder exists inside the notes directory.
    # If not, the repository was never cloned properly, so we must force sync.
    git_folder = os.path.join(paths["notes_dir"], '.git')
    
    if settings.github_repo_url and not os.path.exists(git_folder):
        print(f"Initializing knowledge base for user {request.user.username}...")
        sync_obsidian_repo(settings.github_repo_url, settings.github_token, paths["notes_dir"])

    # Dynamically scan the user's secure directory to find real synced files
    synced_notes = []
    if os.path.exists(paths["notes_dir"]):
        for root, dirs, files in os.walk(paths["notes_dir"]):
            for file in files:
                if file.endswith(".md"):
                    # Strip extension for UI beauty
                    synced_notes.append(file.replace(".md", ""))
                    
    context = {
        'active_page': 'notes', 
        'config': get_user_config(request.user),
        'user_notes': synced_notes[:15] # Send the first 15 files to the template UI
    }
    return render(request, 'notes.html', context)
                    
    context = {
        'active_page': 'notes', 
        'config': get_user_config(request.user),
        'user_notes': synced_notes[:15]
    }
    return render(request, 'notes.html', context)

@login_required(login_url='login')
def tasks_view(request):
    # Fetch tasks for the list view
    tasks = Task.objects.filter(user=request.user)
    context = {
        'active_page': 'tasks', 
        'config': get_user_config(request.user),
        'active_tasks': tasks.exclude(status='done').order_by('due_date'),
        'completed_tasks': tasks.filter(status='done').order_by('-created_at')[:10]
    }
    return render(request, 'tasks.html', context)

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
        
        # FIXED: Passing request.user to preserve multi-tenant security layers
        ai_response = rag_engine.ask_second_brain(user_message, request.user)
        return JsonResponse({'status': 'ok', 'reply': ai_response})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required(login_url='login')
def api_save_settings(request):
    if request.method == "POST":
        data = json.loads(request.body)
        settings = request.user.settings
        
        # Save structural parameters
        settings.display_name = data.get('display_name', settings.display_name)
        settings.theme = data.get('theme', settings.theme)
        settings.accent_color = data.get('accent_color', settings.accent_color)
        settings.ai_model = data.get('ai_model', settings.ai_model)
        settings.temperature = float(data.get('temperature', settings.temperature))
        
        # NEW: Save security validation parameters for RAG Synchronization
        settings.github_repo_url = data.get('github_repo_url', settings.github_repo_url).strip()
        settings.github_token = data.get('github_token', settings.github_token).strip()
        settings.save()
        
        # Clear specific operational in-memory cache matrices for this user
        rag_engine.reset_chat_engine(request.user.id)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required(login_url='login')
def api_add_task(request):
    if request.method == "POST":
        data = json.loads(request.body)
        task = Task.objects.create(
            user=request.user,
            title=data.get('title'),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date') or None,
            tags=data.get('tags', '')
        )
        return JsonResponse({'status': 'ok', 'task_id': task.id})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required(login_url='login')
def api_update_task_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status') # 'todo', 'in_progress', or 'done'
        
        try:
            task = Task.objects.get(id=task_id, user=request.user)
            task.status = new_status
            task.save()
            return JsonResponse({'status': 'ok'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': 'Task not found'}, status=404)
        
        
@login_required(login_url='login')
def api_get_note_content(request):
    """
    API endpoint to fetch and parse a specific Markdown note for the active user.
    Converts raw .md text into HTML for frontend injection.
    """
    from .rag_engine import get_user_paths
    
    note_name = request.GET.get('name')
    if not note_name:
        return JsonResponse({'status': 'error', 'msg': 'No note name provided.'}, status=400)

    paths = get_user_paths(request.user)
    # Ensure the file has the correct markdown extension
    file_name = f"{note_name}.md" 
    file_path = None
    
    # Securely search for the file within the user's isolated directory
    if os.path.exists(paths["notes_dir"]):
        for root, dirs, files in os.walk(paths["notes_dir"]):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                break
                
    if not file_path:
        return JsonResponse({'status': 'error', 'msg': 'Note not found in the secure vault.'}, status=404)

    try:
        # Read raw markdown content
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_markdown = f.read()
            
        # Convert markdown to HTML (enabling extensions for tables, code blocks, etc.)
        html_content = markdown.markdown(raw_markdown, extensions=['fenced_code', 'tables'])
        
        return JsonResponse({
            'status': 'ok',
            'html_content': html_content,
            'last_modified': os.path.getmtime(file_path) # Optional metadata
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)