# Quick Start Guide - Evaluation Project

## Run the Project

### 1. Activate Virtual Environment
```powershell
D:/evaluation_project_source/venv/Scripts/Activate.ps1
```

### 2. Start Development Server
```powershell
python manage.py runserver
```
Or bind to all interfaces:
```powershell
python manage.py runserver 0.0.0.0:8000
```

### 3. Access the Application
- Main site: http://localhost:8000/
- Admin panel: http://localhost:8000/admin/
- Login: admin / (your password)

## Common Commands

### Database
```powershell
# Check migrations
python manage.py showmigrations

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Django shell
python manage.py shell
```

### User Management
```powershell
# Create superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword admin
```

### Static Files
```powershell
# Collect static files
python manage.py collectstatic
```

### Testing
```powershell
# Run system check
python manage.py check

# Run tests
python manage.py test

# Check database connectivity
python test_database.py
```

## Database Configuration
- **Server:** localhost
- **Database:** evaluation_db
- **User:** ali
- **Engine:** MSSQL 2012
- **Driver:** ODBC Driver 17 for SQL Server

## All Tables (20 total)
1. Professor_tbl
2. Participant_tbl
3. Location_tbl
4. Course_tbl
5. Train_tbl
6. Train_Participant_tbl
7. Evaluation_TAB
8. contact_messages
9. user_profiles
10. system_settings
+ 10 Django system tables

## Troubleshooting

### Virtual environment not recognized
Use full path:
```powershell
D:/evaluation_project_source/venv/Scripts/python.exe manage.py runserver
```

### Database connection error
Check settings.py:
- Host: localhost
- Database: evaluation_db
- User credentials
- ODBC Driver installed

### Port already in use
```powershell
python manage.py runserver 8080
```

## Project Status
✅ All migrations applied
✅ All tables created
✅ All relationships configured
✅ Server tested and working
✅ No errors or warnings

**Ready for use!**
