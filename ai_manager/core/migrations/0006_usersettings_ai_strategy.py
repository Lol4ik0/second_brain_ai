from django.db import migrations, models


def migrate_ai_model_to_strategy(apps, schema_editor):
    UserSettings = apps.get_model('core', 'UserSettings')
    mapping = {
        'gemini': 'cloud_only',
        'llama3': 'local_only',
        'phi3': 'local_only',
    }
    for settings in UserSettings.objects.all():
        settings.ai_strategy = mapping.get(settings.ai_model, 'auto')
        settings.save(update_fields=['ai_strategy'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_alter_usersettings_github_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='ai_strategy',
            field=models.CharField(
                choices=[
                    ('auto', 'Auto-Hybrid'),
                    ('local_only', 'Strictly Local'),
                    ('cloud_only', 'Cloud Only'),
                ],
                default='auto',
                max_length=20,
            ),
        ),
        migrations.RunPython(migrate_ai_model_to_strategy, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='usersettings',
            name='ai_model',
        ),
    ]