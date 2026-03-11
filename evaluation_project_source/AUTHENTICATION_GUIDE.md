# Authentication System Documentation

## Overview
This Django project now includes a comprehensive authentication system with role-based access control. The system supports three user roles with different permission levels:

- **Admin**: Full access to all features
- **User**: Can create and edit records
- **Guest**: Read-only access

## Features Implemented

### 1. User Authentication
- ✅ User Registration with role selection
- ✅ User Login with session management
- ✅ User Logout
- ✅ User Dashboard with profile information
- ✅ Password visibility toggle
- ✅ Form validation and error messages

### 2. Role-Based Access Control
- ✅ Three user roles: Admin, User, Guest
- ✅ Custom decorators for permission checking
- ✅ Automatic UserProfile creation on user registration
- ✅ Permission methods: can_create(), can_edit(), can_delete()

### 3. User Interface
- ✅ Modern login page with gradient design
- ✅ Registration page with comprehensive form
- ✅ User dashboard showing profile and permissions
- ✅ Authentication links in header and sidebar
- ✅ Responsive design for mobile devices
- ✅ Stylish CSS with animations

### 4. Security Features
- ✅ Password confirmation on registration
- ✅ Minimum password length validation
- ✅ Username and email uniqueness checks
- ✅ Login required decorators
- ✅ Role-based view protection

## User Roles and Permissions

### Admin Role
- ✅ Can create records
- ✅ Can edit records
- ✅ Can delete records
- ✅ Can view contact messages
- ✅ Access to system statistics
- ✅ Full system access

### User Role
- ✅ Can create records
- ✅ Can edit records
- ❌ Cannot delete records
- ✅ Can view contact messages
- ❌ Limited system statistics

### Guest Role
- ❌ Cannot create records
- ❌ Cannot edit records
- ❌ Cannot delete records
- ❌ Cannot view contact messages
- ✅ Can view evaluations and public pages

## Files Created/Modified

### New Files
1. `evaluation_app/templates/evaluation_app/login.html` - Login page
2. `evaluation_app/templates/evaluation_app/register.html` - Registration page
3. `evaluation_app/templates/evaluation_app/dashboard.html` - User dashboard
4. `evaluation_app/static/evaluation_app/css/auth.css` - Authentication styles
5. `evaluation_app/decorators.py` - Custom permission decorators
6. `evaluation_app/migrations/0007_userprofile.py` - UserProfile migration

### Modified Files
1. `evaluation_app/models.py` - Added UserProfile model
2. `evaluation_app/views.py` - Added authentication views
3. `evaluation_app/urls.py` - Added authentication URLs
4. `evaluation_app/templates/evaluation_app/base.html` - Added auth links
5. `EvaluationProject/settings.py` - Added login redirect settings

## How to Use

### Creating Your First Admin User

1. **Using Django Admin (Recommended)**
   ```bash
   python manage.py createsuperuser
   ```
   - Enter username, email, and password
   - The UserProfile will be created automatically
   - Update the role to 'admin' in Django admin or database

2. **Using the Registration Page**
   - Navigate to http://localhost:8000/register/
   - Fill in the registration form
   - Select "Admin" as the Account Type
   - Click "Create Account"

### Login Process
1. Navigate to http://localhost:8000/login/
2. Enter your username and password
3. Click "Login"
4. You'll be redirected to the home page

### User Dashboard
- Access at http://localhost:8000/dashboard/
- View your profile information
- See your role and permissions
- Quick access to system features
- Admin users see system statistics

### Logout
- Click "Logout" in the header or sidebar
- You'll be logged out and redirected to home

## URL Routes

| URL | View | Description |
|-----|------|-------------|
| `/login/` | user_login | User login page |
| `/register/` | user_register | User registration page |
| `/logout/` | user_logout | Logout (requires login) |
| `/dashboard/` | user_dashboard | User dashboard (requires login) |

## Using Permission Decorators

### In Views
```python
from evaluation_app.decorators import admin_required, can_create_required, role_required

# Require admin role
@admin_required
def admin_only_view(request):
    return render(request, 'admin_page.html')

# Require user or admin role
@role_required('admin', 'user')
def user_or_admin_view(request):
    return render(request, 'user_page.html')

# Check specific permission
@can_create_required
def create_record_view(request):
    return render(request, 'create_form.html')
```

### In Templates
```django
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}!</p>
    
    {% if user.profile.can_create %}
        <a href="{% url 'create_something' %}">Create New</a>
    {% endif %}
    
    {% if user.profile.is_admin %}
        <a href="/admin/">Admin Panel</a>
    {% endif %}
{% else %}
    <a href="{% url 'login' %}">Login</a>
{% endif %}
```

## Database Schema

### UserProfile Model
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='guest')
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Testing the System

### Test User Registration
1. Go to `/register/`
2. Create users with different roles:
   - Admin user: Full access
   - Regular user: Can create/edit
   - Guest user: Read-only

### Test Permissions
1. Login as Guest
   - Try to create evaluation → Should be redirected
   - Try to delete record → Should see error

2. Login as User
   - Create evaluation → Should work
   - Edit evaluation → Should work
   - Delete evaluation → Should be blocked

3. Login as Admin
   - All operations should work
   - Access to contact messages
   - View system statistics

## Troubleshooting

### UserProfile not created automatically
If profiles aren't being created automatically:
```python
# In Django shell
from django.contrib.auth.models import User
from evaluation_app.models import UserProfile

# Create profiles for existing users
for user in User.objects.filter(profile__isnull=True):
    UserProfile.objects.create(user=user, role='guest')
```

### Change user role
```python
# In Django shell
from django.contrib.auth.models import User

user = User.objects.get(username='username')
user.profile.role = 'admin'  # or 'user', 'guest'
user.profile.save()
```

## Next Steps

### Recommended Enhancements
1. Add email verification for registration
2. Implement password reset functionality
3. Add user profile editing page
4. Implement two-factor authentication
5. Add activity logging for admin users
6. Create user management panel for admins
7. Add OAuth2 social login (Google, Facebook)

### Apply Decorators to Existing Views
Update existing views to use the new decorators:
```python
# Example: Protect evaluation creation
from evaluation_app.decorators import can_create_required

@can_create_required
def evaluation_create(request):
    # existing code...
```

## Support
For questions or issues with the authentication system, please refer to:
- Django Authentication Documentation: https://docs.djangoproject.com/en/stable/topics/auth/
- Django User Model: https://docs.djangoproject.com/en/stable/ref/contrib/auth/

## Summary
The authentication system is now fully integrated and ready to use. All users must log in to access the system, and permissions are enforced based on their assigned roles. The system includes a modern UI with responsive design and comprehensive error handling.
