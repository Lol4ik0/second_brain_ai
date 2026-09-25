"""
ASGI config for ai_manager project.

This deployment entry point exposes Django's asynchronous-capable request handler
to ASGI servers; project behavior and middleware are defined in settings.py.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_manager.settings')

application = get_asgi_application()
