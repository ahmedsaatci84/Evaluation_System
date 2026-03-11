@echo off
chcp 65001 >nul
echo ========================================
echo Running Network Access Diagnostics
echo ========================================
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0diagnose_network_access.ps1"
echo.
pause
