from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def role_required(*roles):
    """
    Decorator to check if user has required role.
    Usage: @role_required('admin', 'user')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'profile'):
                user_role = request.user.profile.role
                if user_role in roles:
                    return view_func(request, *args, **kwargs)
            
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator to ensure user is admin.
    Usage: @admin_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.is_admin():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Admin access required.')
        return redirect('home')
    return wrapper


def user_or_admin_required(view_func):
    """
    Decorator to ensure user is either user or admin.
    Usage: @user_or_admin_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            user_role = request.user.profile.role
            if user_role in ['admin', 'user']:
                return view_func(request, *args, **kwargs)
        
        messages.error(request, 'You need user or admin privileges to access this page.')
        return redirect('home')
    return wrapper


def can_create_required(view_func):
    """
    Decorator to check if user can create records.
    Usage: @can_create_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.can_create():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'You do not have permission to create records.')
        return redirect('home')
    return wrapper


def can_edit_required(view_func):
    """
    Decorator to check if user can edit records.
    Usage: @can_edit_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.can_edit():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'You do not have permission to edit records.')
        return redirect('home')
    return wrapper


def can_delete_required(view_func):
    """
    Decorator to check if user can delete records.
    Usage: @can_delete_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.can_delete():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('home')
    return wrapper


def guest_can_create_evaluation(view_func):
    """
    Decorator to allow guest users to only create evaluations.
    Usage: @guest_can_create_evaluation
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            # Allow admin, user, or guest to create evaluations
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'You must be logged in to create evaluations.')
        return redirect('login')
    return wrapper


def not_guest_required(view_func):
    """
    Decorator to prevent guest users from accessing certain views.
    Usage: @not_guest_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            if request.user.profile.role != 'guest':
                return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Guest users cannot access this page. Please contact an administrator for elevated permissions.')
        return redirect('home')
    return wrapper
