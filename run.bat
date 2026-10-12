@echo off
setlocal EnableDelayedExpansion
title AI Data Analyst Agent - Startup Launcher

echo ============================================================
echo           AI DATA ANALYST AGENT - STARTUP LAUNCHER
echo ============================================================
echo.

:: Ensure working directory is the project root
cd /d "%~dp0"
echo [INFO] Working directory: %CD%

:: 1. Check Virtual Environment
if not exist "%~dp0venv\Scripts\activate.bat" (
    echo.
    echo [ERROR] Virtual environment not found at:
    echo         "%~dp0venv"
    echo.
    echo Please create the virtual environment and install dependencies:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call "%~dp0venv\Scripts\activate.bat"
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: 2. Check Python Executable
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not accessible in the virtual environment.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo [INFO] Using %%v

:: 3. Check .env Configuration
if not exist "%~dp0.env" (
    echo.
    echo [WARNING] .env file not found in project root!
    echo           Gemini AI features require GOOGLE_API_KEY in .env
    echo.
) else (
    echo [INFO] Found .env configuration.
)

:: 4. Port Conflict Resolution (Checks ports 8000 and 8501)
set BACKEND_PORT=8000
netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8000 is occupied by another process.
    echo [INFO] Switching Backend to port 8001 as recommended in README.
    set BACKEND_PORT=8001
)

set FRONTEND_PORT=8501
netstat -ano | findstr /R /C:":8501 .*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8501 is occupied by another process.
    echo [INFO] Switching Frontend to port 8502.
    set FRONTEND_PORT=8502
)

:: 5. Launch Backend (FastAPI via Uvicorn)
echo.
echo [INFO] Launching Backend on port !BACKEND_PORT!...
start "AI Data Analyst - Backend" "%~dp0scripts\start_backend.bat" !BACKEND_PORT!

:: 6. Wait for Backend to become ready
echo [INFO] Waiting for Backend to initialize...
set /a attempts=0
:WAIT_BACKEND
powershell -NoProfile -Command "Start-Sleep -Seconds 2"
set /a attempts+=1
curl -s -f http://127.0.0.1:!BACKEND_PORT!/ >nul 2>&1
if errorlevel 1 (
    if !attempts! lss 12 (
        goto WAIT_BACKEND
    ) else (
        echo [WARNING] Backend is taking longer than expected to respond, proceeding with frontend...
    )
) else (
    echo [SUCCESS] Backend is healthy and responding on port !BACKEND_PORT!
)

:: 7. Launch Frontend (Streamlit)
echo.
echo [INFO] Launching Frontend on port !FRONTEND_PORT!...
start "AI Data Analyst - Frontend" "%~dp0scripts\start_frontend.bat" !FRONTEND_PORT! !BACKEND_PORT!

echo.
echo ============================================================
echo   AI DATA ANALYST AGENT IS RUNNING
echo ============================================================
echo   Backend API  : http://127.0.0.1:!BACKEND_PORT!
echo   API Docs     : http://127.0.0.1:!BACKEND_PORT!/docs
echo   Frontend UI  : http://127.0.0.1:!FRONTEND_PORT!
echo ============================================================
echo   [B] Open Frontend in Browser
echo   [D] Open Backend API Docs (Swagger)
echo   [S] Stop all services (kill AI Data Agent processes)
echo   [Q] Close this launcher window (services keep running)
echo ============================================================
echo.

:MENU_LOOP
choice /c BDSQ /n /m "Choose an option [B, D, S, Q]: "
if errorlevel 4 goto EXIT_LAUNCHER
if errorlevel 3 goto STOP_SERVICES
if errorlevel 2 goto OPEN_DOCS
if errorlevel 1 goto OPEN_BROWSER

:OPEN_BROWSER
start http://127.0.0.1:!FRONTEND_PORT!
goto MENU_LOOP

:OPEN_DOCS
start http://127.0.0.1:!BACKEND_PORT!/docs
goto MENU_LOOP

:STOP_SERVICES
echo.
echo [INFO] Stopping AI Data Analyst Backend and Frontend services...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Process -Name python, streamlit -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*AI DATA AGENT*' } | Stop-Process -Force -ErrorAction SilentlyContinue"
echo [INFO] Services stopped.
powershell -NoProfile -Command "Start-Sleep -Seconds 2"
goto EXIT_LAUNCHER

:EXIT_LAUNCHER
echo Exiting launcher...
