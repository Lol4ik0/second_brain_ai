from .auth import register_view, login_view, logout_view
from .pages import home_view, ai_chat_view, notes_view, tasks_view, settings_view
from .api import (api_chat_message, api_save_settings, api_add_task, 
                  api_update_task_status, api_get_note_content, api_sidebar_stats)
from .admin import admin_dashboard_view, api_admin_update_row, api_admin_delete_row