@echo off
title Evaluation App - Update
cd /d D:\evaluation_project_source

echo === Stopping service ===
nssm stop EvaluationApp
timeout /t 2 /nobreak > nul

echo === Installing dependencies ===
venv\Scripts\pip.exe install -r requirements.txt

echo === Running migrations ===
venv\Scripts\python.exe manage.py migrate

echo === Collecting static files ===
venv\Scripts\python.exe manage.py collectstatic --noinput

echo === Starting service ===
nssm start EvaluationApp

echo === Done! App is running at http://localhost:8000 ===
pause
