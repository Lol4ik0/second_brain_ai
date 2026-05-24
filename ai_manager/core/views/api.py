import json
import os
import re
import markdown
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from ..models import Task, ChatMessage
from .. import rag_engine

@csrf_exempt
@login_required(login_url='login')
def api_chat_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if user_message:
            ChatMessage.objects.create(user=request.user, role='user', content=user_message)
            ai_response = rag_engine.ask_second_brain(user_message, request.user)
            ChatMessage.objects.create(user=request.user, role='ai', content=ai_response)
            return JsonResponse({'status': 'ok', 'reply': ai_response})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required(login_url='login')
def api_save_settings(request):
    if request.method == "POST":
        data = json.loads(request.body)
        settings = request.user.settings
        
        settings.display_name = data.get('display_name', settings.display_name)
        settings.theme = data.get('theme', settings.theme)
        settings.accent_color = data.get('accent_color', settings.accent_color)
        settings.ai_model = data.get('ai_model', settings.ai_model)
        settings.temperature = float(data.get('temperature', settings.temperature))
        settings.github_repo_url = data.get('github_repo_url', settings.github_repo_url).strip()
        settings.github_token = data.get('github_token', settings.github_token).strip()
        settings.save()
        
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
        try:
            task = Task.objects.get(id=data.get('task_id'), user=request.user)
            task.status = data.get('status')
            task.save()
            return JsonResponse({'status': 'ok'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': 'Task not found'}, status=404)

@login_required(login_url='login')
def api_get_note_content(request):
    # Твоя большая логика парсинга Obsidian Markdown...
    from ..rag_engine import get_user_paths
    note_name = request.GET.get('name')
    if not note_name:
        return JsonResponse({'status': 'error', 'msg': 'No note name provided.'}, status=400)

    paths = get_user_paths(request.user)
    target_file_name = f"{note_name}.md"
    current_file_path = None
    
    if os.path.exists(paths["notes_dir"]):
        for root, dirs, files in os.walk(paths["notes_dir"]):
            if target_file_name in files:
                current_file_path = os.path.join(root, target_file_name)
                break
                
    if not current_file_path:
        return JsonResponse({'status': 'error', 'msg': 'Note not found in the secure vault.'}, status=404)

    try:
        with open(current_file_path, 'r', encoding='utf-8') as f:
            raw_markdown = f.read()

        linked_mentions = []
        wiki_link_pattern = f"[[{note_name}]]"
        for root, dirs, files in os.walk(paths["notes_dir"]):
            for file in files:
                if file.endswith(".md") and file != target_file_name:
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as sf:
                            scan_content = sf.read()
                            if wiki_link_pattern in scan_content:
                                idx = scan_content.find(wiki_link_pattern)
                                snippet = scan_content[max(0, idx - 40):min(len(scan_content), idx + len(wiki_link_pattern) + 40)].replace('\n', ' ').strip()
                                linked_mentions.append({'title': file.replace(".md", ""), 'snippet': f"...{snippet}..."})
                    except Exception:
                        continue 

        def replace_wiki_links(match):
            link_text = match.group(1).strip()
            if '|' in link_text:
                note_target, note_display = link_text.split('|', 1)
            else:
                note_target, note_display = link_text, link_text
            return f'<a href="#" class="wiki-link text-[var(--active-accent)] border-b border-dashed border-[var(--active-accent)] hover:text-white transition-colors" data-note="{note_target.strip()}">{note_display.strip()}</a>'

        html_content = markdown.markdown(re.sub(r'\[\[(.*?)\]\]', replace_wiki_links, raw_markdown), extensions=['fenced_code', 'tables'])
        return JsonResponse({'status': 'ok', 'html_content': html_content, 'backlinks': linked_mentions})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)

@login_required(login_url='login')
def api_sidebar_stats(request):
    total_tasks = Task.objects.filter(user=request.user).count()
    done_tasks = Task.objects.filter(user=request.user, status='done').count()
    percent = int((done_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    return JsonResponse({'status': 'ok', 'percent': percent, 'done': done_tasks, 'total': total_tasks})