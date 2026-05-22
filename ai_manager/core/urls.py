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
    path('api/get-note/', views.api_get_note_content, name='api_get_note'),
    path('api/sidebar-stats/', views.api_sidebar_stats, name='api_sidebar_stats'),
    
    # NEW TASK APIs
    path('api/add-task/', views.api_add_task, name='api_add_task'),
    path('api/update-task/', views.api_update_task_status, name='api_update_task'),

    # ISOLATED ADMINISTRATIVE PLATFORM ROUTES
    path('system-matrix/', views.admin_dashboard_view, name='admin_dashboard'),
    path('api/admin/update-row/', views.api_admin_update_row, name='api_admin_update'),
    path('api/admin/delete-row/', views.api_admin_delete_row, name='api_admin_delete'),
]