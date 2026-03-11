@echo off

echo Welcome Dear User,
echo ****** Evaluation System Management *****
echo This Software Directed by **** Information Technology Department ****
echo The System Develop By Ahmed Abdulameer Ahmed Saatci

REM Detect local IPv4 address dynamically using PowerShell
for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown' } | Select-Object -First 1).IPAddress"`) do set LOCAL_IP=%%a
echo Detected IP: %LOCAL_IP%

REM Check and start MSSQL$SQLEXPRESS service if not running
echo Checking MSSQL$SQLEXPRESS service...
sc query "MSSQL$SQLEXPRESS" | findstr /i "RUNNING" >nul 2>&1
if %errorlevel% neq 0 (
    echo MSSQL$SQLEXPRESS is not running. Starting service...
    net start "MSSQL$SQLEXPRESS"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to start MSSQL$SQLEXPRESS. The service may not be installed.
    ) else (
        echo MSSQL$SQLEXPRESS started successfully.
        timeout /t 3 /nobreak >nul
    )
) else (
    echo MSSQL$SQLEXPRESS is already running.
)

REM Start the server based on project type
if exist manage.py (
    echo Starting Django server...
    REM Activate virtual environment if it exists
    if exist venv\Scripts\activate.bat (
        echo Activating virtual environment...
        call venv\Scripts\activate.bat
    )
    timeout /t 3 /nobreak >nul
    start http://%LOCAL_IP%:8000/
    python manage.py runserver 0.0.0.0:8000
) else if exist app.py (
    echo Starting Flask server...
    timeout /t 3 /nobreak >nul
    start http://%LOCAL_IP%:8000/
    python app.py --host=0.0.0.0 --port=8000
) else if exist server.js (
    echo Installing npm dependencies...
    call npm install
    echo Starting Node.js server...
    timeout /t 3 /nobreak >nul
    start http://%LOCAL_IP%:8000/
    set PORT=8000
    call npm start
) else if exist package.json (
    echo Installing npm dependencies...
    call npm install
    echo Starting Node.js server...
    timeout /t 3 /nobreak >nul
    start http://%LOCAL_IP%:8000/
    set PORT=8000
    call npm start
) else if exist index.html (
    echo Starting simple HTTP server...
    timeout /t 2 /nobreak >nul
    start http://%LOCAL_IP%:8000/
    python -m http.server 8000 --bind 0.0.0.0
) else (
    echo Could not detect project type
    echo Please run manually
    pause
    exit /b 1
)

