"""Root URL composition for framework administration and the core application."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django's built-in administrative site is mounted separately from Core Matrix.
    path('admin/', admin.site.urls),
    # Delegate application pages and APIs to the core URL namespace.
    path('', include('core.urls')), 
]