@echo off
chcp 65001 >nul
title Evaluation App - Docker

echo ========================================
echo   Evaluation App - Docker Launcher
echo ========================================
echo.

:: ── Check Docker is installed and running ────────────────────────────────────
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not running or not installed.
    echo         Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

:: ── Create .env from template if it does not exist ───────────────────────────
if not exist ".env" (
    if exist ".env.example" (
        echo [SETUP] .env file not found. Creating from .env.example ...
        copy ".env.example" ".env" >nul
        echo.
        echo  *** IMPORTANT: Open .env and set your passwords before continuing! ***
        echo.
        notepad .env
        echo.
        pause
    ) else (
        echo [ERROR] Neither .env nor .env.example found.
        echo         Please create a .env file with your configuration.
        pause
        exit /b 1
    )
)

:: ── Menu ─────────────────────────────────────────────────────────────────────
echo Select an action:
echo.
echo   [1] Start   (build if needed, then run all containers)
echo   [2] Stop    (stop all containers)
echo   [3] Restart (stop then start)
echo   [4] Rebuild (force full image rebuild and start)
echo   [5] Logs    (tail web container logs)
echo   [6] Status  (show running containers)
echo   [7] Pull Ollama model  (run after first start)
echo   [8] Exit
echo.
set /p CHOICE="Enter choice [1-8]: "

if "%CHOICE%"=="1" goto START
if "%CHOICE%"=="2" goto STOP
if "%CHOICE%"=="3" goto RESTART
if "%CHOICE%"=="4" goto REBUILD
if "%CHOICE%"=="5" goto LOGS
if "%CHOICE%"=="6" goto STATUS
if "%CHOICE%"=="7" goto PULLMODEL
if "%CHOICE%"=="8" goto END

echo [ERROR] Invalid choice. Please run the script again.
pause
goto END

:: ── Actions ──────────────────────────────────────────────────────────────────

:START
echo.
echo [START] Starting all containers ...
docker compose up -d
echo.
echo App is running at: http://localhost:8000
goto END

:STOP
echo.
echo [STOP] Stopping all containers ...
docker compose down
goto END

:RESTART
echo.
echo [RESTART] Stopping containers ...
docker compose down
echo [RESTART] Starting containers ...
docker compose up -d
echo.
echo App is running at: http://localhost:8000
goto END

:REBUILD
echo.
echo [REBUILD] Rebuilding image and restarting ...
docker compose down
docker compose up -d --build
echo.
echo App is running at: http://localhost:8000
goto END

:LOGS
echo.
echo [LOGS] Tailing web container logs (Ctrl+C to stop) ...
docker compose logs -f web
goto END

:STATUS
echo.
docker compose ps
goto END

:PULLMODEL
echo.
set /p MODEL="Enter Ollama model name to pull [default: llama3.2]: "
if "%MODEL%"=="" set MODEL=llama3.2
echo [OLLAMA] Pulling model: %MODEL% (this may take several minutes) ...
docker exec evaluation_ollama ollama pull %MODEL%
goto END

:END
echo.
pause
