from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings
import base64

# --- SECURITY ENGINE: CUSTOM ENCRYPTION FIELD ---
def get_fernet():
    """
    Генерирует уникальный ключ шифрования на основе SECRET_KEY твоего Django проекта.
    Даже если украдут базу данных, без файла .env расшифровать токены будет невозможно.
    """
    key = settings.SECRET_KEY.encode('utf-8')[:32].ljust(32, b'0')
    return Fernet(base64.urlsafe_b64encode(key))

class EncryptedCharField(models.CharField):
    """
    Custom database field that transparently encrypts text when saving and decrypts it when reading in Python.
    This ensures that sensitive data like GitHub tokens are stored securely in the database.
    """
    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return get_fernet().decrypt(value.encode('utf-8')).decode('utf-8')
        except Exception:
            return value

    def get_prep_value(self, value):
        if not value:
            return value
        if value.startswith('gAAAAAB'):
            return value
        return get_fernet().encrypt(value.encode('utf-8')).decode('utf-8')

# --- DATABASE MODELS ---

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    display_name = models.CharField(max_length=100, blank=True)
    theme = models.CharField(max_length=20, default='cyberpunk')
    accent_color = models.CharField(max_length=20, default='cyan')
    ai_model = models.CharField(max_length=50, default='llama3')
    temperature = models.FloatField(default=0.7)

    github_repo_url = models.URLField(max_length=500, blank=True, default="")
    github_token = EncryptedCharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"Settings for {self.user.username}"

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True)
    tags = models.CharField(max_length=100, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
    
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=10) 
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] 

    def __str__(self):
        return f"{self.user.username} - {self.role}: {self.content[:20]}"

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(
            user=instance, 
            display_name=instance.username,
            theme='cyberpunk',
            accent_color='cyan',
            ai_model='llama3',
            temperature=0.7,
            github_repo_url="",
            github_token=""
        )