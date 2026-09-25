"""Django application registration metadata for the core workspace app."""
from django.apps import AppConfig

class CoreConfig(AppConfig):
    # Use wide primary keys by default for newly declared application models.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'