# System Close/Open Feature Documentation

## Overview
The System Close/Open feature allows administrators to temporarily close the evaluation system for maintenance or other purposes. When the system is closed, regular users will see a maintenance page while administrators can still access the system (if configured).

## Features
- **Toggle System Status**: Quickly open or close the system with one click
- **Custom Closure Message**: Set a custom message to display when system is closed
- **Scheduled Closure**: Set an expected end date for the closure
- **Admin Access Control**: Choose whether admins can access during closure
- **Automatic Redirect**: Non-admin users are automatically redirected to maintenance page

## How to Use

### For Administrators

#### Quick Toggle (Dashboard)
1. Log in as an administrator
2. Go to your Dashboard
3. In the "System Control Panel" section, you'll see the current system status
4. Click "Close System" or "Open System" button
5. Confirm the action in the popup dialog

#### Full System Settings Management
1. Log in as an administrator
2. Go to Dashboard → Click "Manage Settings" button
   OR navigate to `/system-settings/`
3. Configure the following options:
   - **Keep System Open**: Toggle to open/close the system
   - **Closure Message**: Enter a message to display to users
   - **Expected Closure End**: Set when you expect to reopen
   - **Allow Admin Access**: Choose if admins can access during closure
4. Click "Save Settings"

#### Via Django Admin
1. Access the Django admin panel at `/admin/`
2. Navigate to "System Settings"
3. Modify the settings as needed
4. Save changes

### What Happens When System is Closed

**For Regular Users:**
- Redirected to a maintenance page
- Cannot access any part of the system
- See the custom closure message
- See expected reopening date (if set)

**For Administrators (if admin access is enabled):**
- Can still access all parts of the system
- See a warning indicator that system is closed
- Can manage and reopen the system

### URLs
- **System Settings Management**: `/system-settings/`
- **Toggle Status**: `/toggle-system-status/`
- **Maintenance Page**: `/system-closed/`

## Technical Details

### Database Model
- **Model**: `SystemSettings`
- **Table**: `system_settings`
- **Pattern**: Singleton (only one instance allowed)

### Fields
- `is_system_open`: Boolean - System status
- `closure_message`: Text - Message to display
- `closure_start_date`: DateTime - When closure started
- `closure_end_date`: DateTime - Expected end of closure
- `allow_admin_access`: Boolean - Admin access during closure
- `last_updated`: DateTime - Last modification time
- `updated_by`: ForeignKey(User) - Who made the last change

### Middleware
`SystemStatusMiddleware` checks every request and redirects to maintenance page if:
- System is closed
- User is not an admin (or admin access is disabled)
- Request is not for an allowed URL (admin, static files, etc.)

### Allowed URLs During Closure
- `/admin/` - Django admin panel
- `/set-language/` - Language switcher
- `/system-closed/` - Maintenance page
- `/static/` - Static files
- `/media/` - Media files

## Security Considerations

1. **Admin Only**: Only users with admin role can change system status
2. **Confirmation Required**: Toggle actions require confirmation
3. **Audit Trail**: Tracks who made changes and when
4. **Safe Defaults**: System opens by default, admin access allowed

## Best Practices

1. **Notify Users**: Set a clear closure message explaining the reason
2. **Set End Date**: Provide an expected reopening time
3. **Test First**: Test the closure with admin access enabled first
4. **Plan Ahead**: Schedule closures during low-usage periods
5. **Quick Reopening**: Keep admin access enabled for quick fixes

## Troubleshooting

### Can't Access System After Closure
- Access via `/admin/` panel
- Log in as superuser or admin
- Navigate to System Settings and reopen

### Changes Not Taking Effect
- Clear browser cache
- Check middleware is enabled in settings.py
- Verify database migration ran successfully

### Admin Can't Access During Closure
- Check "Allow Admin Access" is enabled
- Verify user has admin role in UserProfile
- Check if user is superuser or staff

## Migration
Run the migration to create the SystemSettings table:
```bash
python manage.py migrate evaluation_app
```

## Initial Setup
The system settings will be created automatically on first access. Default values:
- System: Open
- Admin Access: Allowed
- Message: Default maintenance message
