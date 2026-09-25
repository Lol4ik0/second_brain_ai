"""
WSGI config for ai_manager project.

This deployment entry point exposes Django's synchronous request handler to WSGI
servers; project behavior and middleware are defined in settings.py.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_manager.settings')

application = get_wsgi_application()
