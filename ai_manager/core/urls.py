from django.urls import path
from . import views 

urlpatterns = [
    # Auth endpoints
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Workspace endpoints
    path('', views.home_view, name='home'),
    path('chat/', views.ai_chat_view, name='chat'),
    path('notes/', views.notes_view, name='notes'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('settings/', views.settings_view, name='settings'),
    
    # API endpoints
    path('api/send-message/', views.api_chat_message, name='api_send_message'),
    path('api/save-settings/', views.api_save_settings, name='api_save_settings'),
    
    # NEW TASK APIs
    path('api/add-task/', views.api_add_task, name='api_add_task'),
    path('api/update-task/', views.api_update_task_status, name='api_update_task'),
]