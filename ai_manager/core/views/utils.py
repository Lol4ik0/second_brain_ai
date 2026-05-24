def get_user_config(user):
    if user.is_authenticated:
        return user.settings
    return {
        "display_name": "Guest Traveler",
        "email": "",
        "theme": "cyberpunk",
        "accent_color": "cyan",
        "ai_model": "llama3",
        "temperature": "0.7"
    }