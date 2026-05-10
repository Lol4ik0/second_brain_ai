from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home_view, name='home'),
    path('chat/', views.ai_chat_view, name='chat'),
    path('notes/', views.notes_view, name='notes'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('settings/', views.settings_view, name='settings'),
    
    path('api/send-message/', views.api_chat_message, name='api_send_message'),
]