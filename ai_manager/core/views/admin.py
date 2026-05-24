import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

from ..models import UserSettings, Task, ChatMessage

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_dashboard_view(request):
    context = {
        'users': User.objects.all().order_by('id'),
        'settings': UserSettings.objects.all().order_by('id'),
        'tasks': Task.objects.all().order_by('-id'),
        'messages': ChatMessage.objects.all().order_by('-id')[:100],
    }
    return render(request, 'admin_dashboard.html', context)

@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def api_admin_update_row(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            target_table, row_id, fields = data.get('table'), data.get('id'), data.get('fields', {})

            if target_table == 'users':
                obj = User.objects.get(id=row_id)
                obj.username, obj.email = fields.get('username', obj.username), fields.get('email', obj.email)
                obj.is_superuser = fields.get('is_superuser') in ['true', True]
                obj.save()
            elif target_table == 'settings':
                obj = UserSettings.objects.get(id=row_id)
                for f in ['display_name', 'theme', 'accent_color', 'ai_model', 'github_repo_url']:
                    setattr(obj, f, fields.get(f, getattr(obj, f)))
                obj.temperature = float(fields.get('temperature', obj.temperature))
                obj.save()
            elif target_table == 'tasks':
                obj = Task.objects.get(id=row_id)
                for f in ['title', 'status', 'priority', 'tags']:
                    setattr(obj, f, fields.get(f, getattr(obj, f)))
                obj.due_date = fields.get('due_date') or None
                obj.save()
            elif target_table == 'messages':
                obj = ChatMessage.objects.get(id=row_id)
                obj.role, obj.content = fields.get('role', obj.role), fields.get('content', obj.content)
                obj.save()
            else:
                return JsonResponse({'status': 'error', 'msg': 'Target table unrecognized.'}, status=400)
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def api_admin_delete_row(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            models_map = {'users': User, 'settings': UserSettings, 'tasks': Task, 'messages': ChatMessage}
            if data.get('table') in models_map:
                models_map[data.get('table')].objects.filter(id=data.get('id')).delete()
                return JsonResponse({'status': 'ok'})
            return JsonResponse({'status': 'error', 'msg': 'Invalid model context.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)