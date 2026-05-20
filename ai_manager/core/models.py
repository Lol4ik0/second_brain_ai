from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserSettings(models.Model):
    # Link each settings row directly to a user account
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # Profile information
    display_name = models.CharField(max_length=100, blank=True)
    
    # Appearance states
    theme = models.CharField(max_length=20, default='cyberpunk')
    accent_color = models.CharField(max_length=20, default='cyan')
    
    # AI Config elements
    ai_model = models.CharField(max_length=50, default='llama3')
    temperature = models.FloatField(default=0.7)

    def __str__(self):
        return f"Settings for {self.user.username}"

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
            temperature=0.7
        )