import os
from datetime import datetime
from collections import Counter
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware

from ..models import Task, ChatMessage
from .. import rag_engine
from .utils import get_user_config

@login_required(login_url='login')
def home_view(request):
    from ..rag_engine import get_user_paths
    tasks = Task.objects.filter(user=request.user)
    
    top_focus = "General Systems"
    active_tags = tasks.exclude(status='done').exclude(tags__exact='').values_list('tags', flat=True)
    if active_tags:
        all_tags = [tag.strip() for tags_str in active_tags for tag in tags_str.split(',')]
        if all_tags:
            top_focus = Counter(all_tags).most_common(1)[0][0]

    paths = get_user_paths(request.user)
    recent_notes = []
    
    if os.path.exists(paths["notes_dir"]):
        for root, dirs, files in os.walk(paths["notes_dir"]):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    mtime = os.path.getmtime(file_path)
                    dt_mtime = make_aware(datetime.fromtimestamp(mtime))
                    recent_notes.append({'name': file.replace('.md', ''), 'modified_at': dt_mtime})
                    
    recent_notes.sort(key=lambda x: x['modified_at'], reverse=True)
    top_recent_notes = recent_notes[:3]

    context = {
        'active_page': 'home', 
        'config': get_user_config(request.user),
        'todo_tasks': tasks.filter(status='todo'),
        'progress_tasks': tasks.filter(status='in_progress'),
        'done_tasks': tasks.filter(status='done'),
        'recent_tasks': tasks.order_by('-created_at')[:4],
        'recent_notes': top_recent_notes,
        'total_notes_count': len(recent_notes),
        'top_focus': top_focus
    }
    return render(request, 'home.html', context)

@login_required(login_url='login')
def ai_chat_view(request):
    from ..rag_engine import get_user_paths
    paths = get_user_paths(request.user)
    synced_notes = []
    if os.path.exists(paths["notes_dir"]):
        for root, dirs, files in os.walk(paths["notes_dir"]):
            for file in files:
                if file.endswith(".md"):
                    synced_notes.append(file.replace(".md", ""))
                    
    chat_history = reversed(ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:50])
    context = {
        'active_page': 'ai-chat', 
        'config': get_user_config(request.user),
        'context_files': synced_notes[:10],
        'chat_history': chat_history
    }
    return render(request, 'ai-chat.html', context)

@login_required(login_url='login')
def notes_view(request):
    import os
    from ..rag_engine import get_user_paths
    from ..git_sync import sync_obsidian_repo
    
    paths = get_user_paths(request.user)
    settings = request.user.settings
    git_folder = os.path.join(paths["notes_dir"], '.git')
    
    if settings.github_repo_url and not os.path.exists(git_folder):
        sync_obsidian_repo(settings.github_repo_url, settings.github_token, paths["notes_dir"])

    synced_notes = []
    if os.path.exists(paths["notes_dir"]):
        for root, dirs, files in os.walk(paths["notes_dir"]):
            for file in files:
                if file.endswith(".md"):
                    synced_notes.append(file.replace(".md", ""))
                    
    return render(request, 'notes.html', {
        'active_page': 'notes', 
        'config': get_user_config(request.user),
        'user_notes': synced_notes
    })

@login_required(login_url='login')
def tasks_view(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks.html', {
        'active_page': 'tasks', 
        'config': get_user_config(request.user),
        'active_tasks': tasks.exclude(status='done').order_by('due_date'),
        'completed_tasks': tasks.filter(status='done').order_by('-created_at')[:10]
    })

@login_required(login_url='login')
def settings_view(request):
    return render(request, 'settings.html', {'active_page': 'settings', 'config': get_user_config(request.user)})