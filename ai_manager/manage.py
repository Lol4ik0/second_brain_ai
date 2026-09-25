#!/usr/bin/env python
"""Django command entry point for migrations, checks, and local server operations."""
import os
import sys


def main():
    """Load the project settings and delegate arguments to Django's CLI dispatcher."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_manager.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
