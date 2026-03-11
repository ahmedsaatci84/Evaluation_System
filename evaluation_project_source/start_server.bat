@echo off
chcp 65001 >nul
for /f "delims=" %%i in ('powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -ne ''127.0.0.1'' } | Select-Object -First 1 -ExpandProperty IPAddress)"') do set LOCAL_IP=%%i
if "%LOCAL_IP%"=="" set LOCAL_IP=127.0.0.1
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
