"""
Context processors for evaluation_app.
These functions add variables to the template context for all templates.
"""
from .models import SystemSettings


def system_settings(request):
    """
    Add system settings to the template context.
    This makes system settings available in all templates.
    """
    try:
        settings = SystemSettings.get_settings()
        return {
            'system_settings': settings
        }
    except Exception:
        # If settings don't exist or database error, return empty dict
        return {
            'system_settings': None
        }
