@echo off
chcp 65001 >nul
set LOCAL_IP=192.168.3.3:8000
echo ========================================
echo Starting Django Development Server
echo ========================================
echo.
echo The server will be accessible at:
echo   - Local:    http://localhost:8000
echo   - Network:  http://%LOCAL_IP%:8000
echo.
echo IMPORTANT: Make sure Windows Firewall allows port 8000
echo Run 'allow_firewall.ps1' as Administrator if needed
echo.
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000
