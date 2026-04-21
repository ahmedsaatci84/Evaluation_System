from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from ..models import SystemSettings


def system_closed(request):
    sys_settings = SystemSettings.get_settings()
    return render(request, 'evaluation_app/system/closed.html', {
        'settings': sys_settings,
        'closure_message': sys_settings.closure_message or 'The system is currently closed for maintenance.',
        'closure_end_date': sys_settings.closure_end_date,
    })


@login_required
def toggle_system_status(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin():
        messages.error(request, 'You do not have permission to manage system status.')
        return redirect('home')
    sys_settings = SystemSettings.get_settings()
    sys_settings.is_system_open = not sys_settings.is_system_open
    sys_settings.updated_by = request.user
    if not sys_settings.is_system_open:
        sys_settings.closure_start_date = timezone.now()
    sys_settings.save()
    status = "opened" if sys_settings.is_system_open else "closed"
    messages.success(request, f'System has been {status} successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def manage_system_settings(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin():
        messages.error(request, 'You do not have permission to manage system settings.')
        return redirect('home')
    sys_settings = SystemSettings.get_settings()
    if request.method == 'POST':
        sys_settings.is_system_open = request.POST.get('is_system_open') == 'on'
        sys_settings.closure_message = request.POST.get('closure_message', '')
        sys_settings.allow_admin_access = request.POST.get('allow_admin_access') == 'on'
        closure_end_date = request.POST.get('closure_end_date')
        if closure_end_date:
            from datetime import datetime
            try:
                sys_settings.closure_end_date = timezone.make_aware(
                    datetime.strptime(closure_end_date, '%Y-%m-%dT%H:%M')
                )
            except ValueError:
                pass
        if not sys_settings.is_system_open:
            if not sys_settings.closure_start_date:
                sys_settings.closure_start_date = timezone.now()
        else:
            sys_settings.closure_start_date = None
        sys_settings.updated_by = request.user
        sys_settings.save()
        messages.success(request, 'System settings updated successfully.')
        return redirect('manage_system_settings')
    return render(request, 'evaluation_app/system/settings.html', {'settings': sys_settings})
