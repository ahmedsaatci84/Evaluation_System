@echo off
title Evaluation App - Waitress Server
cd /d D:\evaluation_project_source

echo Starting Evaluation App on http://0.0.0.0:8000 ...
venv\Scripts\waitress-serve.exe --port=8000 --threads=4 --host=0.0.0.0 EvaluationProject.wsgi:application
