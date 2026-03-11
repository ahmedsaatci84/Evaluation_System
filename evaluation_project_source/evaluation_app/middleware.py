from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .models import SystemSettings


class SystemStatusMiddleware(MiddlewareMixin):
    """
    Middleware to check if the system is open or closed.
    If closed, redirect users to a maintenance page (except admins if configured).
    """
    
    # URLs that should always be accessible even when system is closed
    ALLOWED_URLS = [
        '/admin/',  # Django admin
        '/set-language/',  # Language switcher
        '/system-closed/',  # System closed page
        '/static/',  # Static files
        '/media/',  # Media files
    ]
    
    def process_request(self, request):
        # Skip middleware for allowed URLs
        if any(request.path.startswith(url) for url in self.ALLOWED_URLS):
            return None
        
        # Get system settings
        try:
            settings = SystemSettings.get_settings()
        except Exception:
            # If settings don't exist or database error, allow access
            return None
        
        # If system is open, allow access
        if settings.is_system_open:
            return None
        
        # If system is closed, check if admin access is allowed
        if settings.allow_admin_access and request.user.is_authenticated:
            # Check if user is admin
            if hasattr(request.user, 'profile') and request.user.profile.is_admin():
                return None
            # Also allow Django superusers
            if request.user.is_superuser or request.user.is_staff:
                return None
        
        # System is closed, redirect to closed page
        if request.path != reverse('system_closed'):
            return redirect('system_closed')
        
        return None
