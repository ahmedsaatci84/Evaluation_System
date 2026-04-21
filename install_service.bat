@echo off
title Install EvaluationApp as Windows Service
cd /d D:\evaluation_project_source

:: Must run as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator.
    pause
    exit /b 1
)

:: Check nssm is available
where nssm >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: nssm.exe not found in PATH.
    echo Download it from https://nssm.cc/download and copy nssm.exe to C:\Windows\System32\
    pause
    exit /b 1
)

echo === Installing EvaluationApp as Windows Service ===

nssm install EvaluationApp "D:\evaluation_project_source\venv\Scripts\waitress-serve.exe"
nssm set EvaluationApp AppParameters "--port=8000 --threads=4 --host=0.0.0.0 EvaluationProject.wsgi:application"
nssm set EvaluationApp AppDirectory "D:\evaluation_project_source"
nssm set EvaluationApp DisplayName "Evaluation App"
nssm set EvaluationApp Description "Django Evaluation Project served by Waitress"
nssm set EvaluationApp Start SERVICE_AUTO_START
nssm set EvaluationApp AppStdout "D:\evaluation_project_source\logs\service.log"
nssm set EvaluationApp AppStderr "D:\evaluation_project_source\logs\service_error.log"
nssm set EvaluationApp AppRotateFiles 1
nssm set EvaluationApp AppRotateBytes 5242880

:: Create logs folder
if not exist "D:\evaluation_project_source\logs" mkdir "D:\evaluation_project_source\logs"

echo === Starting service ===
nssm start EvaluationApp

echo.
echo === Done! ===
echo Service installed and started.
echo App is accessible at http://localhost:8000
echo To manage: use 'nssm start/stop/restart EvaluationApp' (as Administrator)
pause
