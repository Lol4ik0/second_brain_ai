from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    display_name = models.CharField(max_length=100, blank=True)
    theme = models.CharField(max_length=20, default='cyberpunk')
    accent_color = models.CharField(max_length=20, default='cyan')
    ai_model = models.CharField(max_length=50, default='llama3')
    temperature = models.FloatField(default=0.7)

    github_repo_url = models.URLField(max_length=500, blank=True, default="")
    github_token = models.CharField(max_length=255, blank=True, default="")

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
    role = models.CharField(max_length=10) # Будет хранить 'user' или 'ai'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Сообщения всегда будут по порядку времени

    def __str__(self):
        return f"{self.user.username} - {self.role}: {self.content[:20]}"

# AUTOMATIC SIGNAL: Whenever a new User is created, automatically build their UserSettings profile row
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