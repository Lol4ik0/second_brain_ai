"""Shared view helpers for exposing authenticated settings to templates."""
# Return the related settings model for signed-in users and a safe display-only
# fallback mapping for anonymous contexts.
# Parameters: user is the Django request user supplied by the calling view.
# Returns: UserSettings for authenticated accounts, otherwise guest defaults.
def get_user_config(user):
    if user.is_authenticated:
        return user.settings
    return {
        "display_name": "Guest Traveler",
        "email": "",
        "theme": "cyberpunk",
        "accent_color": "cyan",
        "ai_strategy": "auto",
        "temperature": "0.7"
    }