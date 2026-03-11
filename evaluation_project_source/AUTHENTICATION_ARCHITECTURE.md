# Authentication System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION SYSTEM                         │
│                    Evaluation Project                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         USER ROLES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │    ADMIN    │    │     USER    │    │    GUEST    │        │
│  ├─────────────┤    ├─────────────┤    ├─────────────┤        │
│  │ ✓ Create    │    │ ✓ Create    │    │ ✗ Create    │        │
│  │ ✓ Edit      │    │ ✓ Edit      │    │ ✗ Edit      │        │
│  │ ✓ Delete    │    │ ✗ Delete    │    │ ✗ Delete    │        │
│  │ ✓ View All  │    │ ✓ View All  │    │ ✓ View All  │        │
│  │ ✓ Contacts  │    │ ✓ Contacts  │    │ ✗ Contacts  │        │
│  │ ✓ Stats     │    │ ✗ Stats     │    │ ✗ Stats     │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      AUTHENTICATION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Visitor    │
    └──────┬───────┘
           │
           ├──────────┐
           │          │
    ┌──────▼──────┐  │
    │   /login/   │  │
    │             │  │
    │  Username   │  │
    │  Password   │  │
    └──────┬──────┘  │
           │         │
    ┌──────▼──────┐  │
    │  Validate   │  │
    │ Credentials │  │
    └──────┬──────┘  │
           │         │
      ┌────▼────┐    │
      │ Valid?  │    │
      └────┬────┘    │
           │         │
      ┌────▼────┐    │
      │  YES    │    │
      └────┬────┘    │
           │         │
    ┌──────▼──────┐  │
    │ Create      │  │
    │ Session     │  │
    └──────┬──────┘  │
           │         │
    ┌──────▼──────┐  │
    │ Load User   │  │
    │ Profile &   │  │
    │ Permissions │  │
    └──────┬──────┘  │
           │         │
    ┌──────▼──────┐  │
    │  Redirect   │  │
    │  to Home    │  │
    └─────────────┘  │
                     │
                ┌────▼────┐
                │   NO    │
                └────┬────┘
                     │
              ┌──────▼──────┐
              │Show Error   │
              │Message      │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │Return to    │
              │Login Page   │
              └─────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                             │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ New Visitor  │
    └──────┬───────┘
           │
    ┌──────▼──────────┐
    │  /register/     │
    │                 │
    │  Username       │
    │  Email          │
    │  Password       │
    │  Confirm Pass   │
    │  First Name     │
    │  Last Name      │
    │  Phone          │
    │  Role Selection │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │  Validate Form  │
    │                 │
    │  ✓ Required     │
    │  ✓ Unique       │
    │  ✓ Password     │
    │  ✓ Match        │
    └──────┬──────────┘
           │
      ┌────▼────┐
      │ Valid?  │
      └────┬────┘
           │
      ┌────▼────┐
      │  YES    │
      └────┬────┘
           │
    ┌──────▼──────────┐
    │  Create User    │
    │  (Django Auth)  │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │  Create Profile │
    │  (Auto Signal)  │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │  Set Role &     │
    │  Phone          │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │  Success!       │
    │  Redirect to    │
    │  Login          │
    └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐         ┌──────────────────────────┐
│   auth_user (Django)    │         │   UserProfile (Custom)   │
├─────────────────────────┤         ├──────────────────────────┤
│ id (PK)                 │◄────┐   │ id (PK)                  │
│ username (UNIQUE)       │     │   │ user_id (FK) (UNIQUE)    │
│ email (UNIQUE)          │     └───┤ role (admin/user/guest)  │
│ password (HASHED)       │         │ phone                    │
│ first_name              │         │ created_at               │
│ last_name               │         │ updated_at               │
│ is_staff                │         └──────────────────────────┘
│ is_active               │
│ date_joined             │         Relationship: One-to-One
└─────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   PERMISSION DECORATORS                          │
└─────────────────────────────────────────────────────────────────┘

@login_required              - Must be logged in
@admin_required              - Must be admin role
@user_or_admin_required      - Must be user or admin
@role_required('admin')      - Specific role(s)
@can_create_required         - Check create permission
@can_edit_required           - Check edit permission
@can_delete_required         - Check delete permission

┌─────────────────────────────────────────────────────────────────┐
│                      URL STRUCTURE                               │
└─────────────────────────────────────────────────────────────────┘

/                           → Home (index)
/login/                     → Login page
/register/                  → Registration page
/logout/                    → Logout (requires login)
/dashboard/                 → User dashboard (requires login)

/evaluations/               → List evaluations
/evaluations/create/        → Create (requires can_create)
/evaluations/<id>/update/   → Edit (requires can_edit)
/evaluations/<id>/delete/   → Delete (requires can_delete)

[Similar patterns for professors, courses, participants, locations]

┌─────────────────────────────────────────────────────────────────┐
│                    ACCESS CONTROL MATRIX                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┬───────┬──────┬───────┐
│      Feature        │ Admin │ User │ Guest │
├─────────────────────┼───────┼──────┼───────┤
│ View Evaluations    │   ✓   │  ✓   │   ✓   │
│ Create Evaluation   │   ✓   │  ✓   │   ✗   │
│ Edit Evaluation     │   ✓   │  ✓   │   ✗   │
│ Delete Evaluation   │   ✓   │  ✗   │   ✗   │
│ View Professors     │   ✓   │  ✓   │   ✓   │
│ Manage Professors   │   ✓   │  ✓   │   ✗   │
│ View Courses        │   ✓   │  ✓   │   ✓   │
│ Manage Courses      │   ✓   │  ✓   │   ✗   │
│ View Participants   │   ✓   │  ✓   │   ✓   │
│ Manage Participants │   ✓   │  ✓   │   ✗   │
│ View Locations      │   ✓   │  ✓   │   ✓   │
│ Manage Locations    │   ✓   │  ✓   │   ✗   │
│ View Contacts       │   ✓   │  ✓   │   ✗   │
│ Delete Contacts     │   ✓   │  ✗   │   ✗   │
│ System Stats        │   ✓   │  ✗   │   ✗   │
│ User Dashboard      │   ✓   │  ✓   │   ✓   │
│ Django Admin        │   ✓*  │  ✗   │   ✗   │
└─────────────────────┴───────┴──────┴───────┘

* Requires is_staff or is_superuser flag

┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY FEATURES                            │
└─────────────────────────────────────────────────────────────────┘

✓ Password hashing (Django PBKDF2)
✓ Session management
✓ CSRF protection
✓ SQL injection protection (Django ORM)
✓ XSS protection (Django templates)
✓ Password length validation
✓ Password confirmation check
✓ Username uniqueness check
✓ Email uniqueness check
✓ Role-based access control
✓ Login required decorators
✓ Permission checking methods
✓ Secure logout
✓ Automatic profile creation

┌─────────────────────────────────────────────────────────────────┐
│                   COMPONENT ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
├────────────────────────────────────────────────────────────┤
│  login.html  │  register.html  │  dashboard.html          │
│  base.html (header with auth links, sidebar navigation)    │
│  auth.css (modern gradient styles, animations)             │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                     CONTROLLER LAYER                        │
├────────────────────────────────────────────────────────────┤
│  views.py                                                   │
│  ├─ user_login()      - Handle login                       │
│  ├─ user_register()   - Handle registration                │
│  ├─ user_logout()     - Handle logout                      │
│  └─ user_dashboard()  - User profile page                  │
│                                                             │
│  decorators.py                                              │
│  ├─ @admin_required                                         │
│  ├─ @role_required()                                        │
│  ├─ @can_create_required                                    │
│  ├─ @can_edit_required                                      │
│  └─ @can_delete_required                                    │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                      MODEL LAYER                            │
├────────────────────────────────────────────────────────────┤
│  models.py                                                  │
│  ├─ UserProfile                                             │
│  │  ├─ user (OneToOne → User)                             │
│  │  ├─ role (admin/user/guest)                            │
│  │  ├─ phone                                               │
│  │  ├─ is_admin()                                          │
│  │  ├─ can_create()                                        │
│  │  ├─ can_edit()                                          │
│  │  └─ can_delete()                                        │
│  │                                                          │
│  └─ Signals                                                 │
│     ├─ create_user_profile (post_save)                     │
│     └─ save_user_profile (post_save)                       │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                           │
├────────────────────────────────────────────────────────────┤
│  auth_user  │  user_profiles  │  other tables             │
└────────────────────────────────────────────────────────────┘
```

## Test Credentials

```
┌──────────────────────────────────────────────────────┐
│               TEST USER ACCOUNTS                      │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ADMIN:                                              │
│  Username: admin_user                                │
│  Password: admin123                                  │
│  Role: Administrator (Full Access)                   │
│                                                       │
│  USER:                                               │
│  Username: regular_user                              │
│  Password: user123                                   │
│  Role: Regular User (Create & Edit)                 │
│                                                       │
│  GUEST:                                              │
│  Username: guest_user                                │
│  Password: guest123                                  │
│  Role: Guest (Read Only)                            │
│                                                       │
└──────────────────────────────────────────────────────┘
```
