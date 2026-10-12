@echo off
title AI Data Analyst - Frontend (Streamlit)
cd /d "%~dp0.."

echo ============================================================
echo   AI DATA ANALYST - FRONTEND (Streamlit)
echo ============================================================
echo.

if not exist "%~dp0..\venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at %~dp0..\venv
    pause
    exit /b 1
)

call "%~dp0..\venv\Scripts\activate.bat"

set PORT=%~1
if "%PORT%"=="" set PORT=8501

set BACKEND_PORT=%~2
if "%BACKEND_PORT%"=="" set BACKEND_PORT=8000

set "API_URL=http://127.0.0.1:%BACKEND_PORT%"

echo [INFO] Starting Frontend on http://127.0.0.1:%PORT% ...
echo [INFO] Target Backend API: %API_URL%
echo.

streamlit run frontend\app.py --server.port %PORT%
if errorlevel 1 (
    echo.
    echo [ERROR] Frontend process terminated unexpectedly.
    pause
)
