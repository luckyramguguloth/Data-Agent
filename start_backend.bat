@echo off
title AI Data Analyst - Backend (FastAPI)
cd /d "%~dp0.."

echo ============================================================
echo   AI DATA ANALYST - BACKEND (FastAPI)
echo ============================================================
echo.

if not exist "%~dp0..\venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at %~dp0..\venv
    pause
    exit /b 1
)

call "%~dp0..\venv\Scripts\activate.bat"

set PORT=%~1
if "%PORT%"=="" set PORT=8000

echo [INFO] Starting Backend on http://127.0.0.1:%PORT% ...
echo [INFO] Interactive Swagger Docs available at http://127.0.0.1:%PORT%/docs
echo.

python -m uvicorn backend.app:app --host 127.0.0.1 --port %PORT% --reload
if errorlevel 1 (
    echo.
    echo [ERROR] Backend process terminated unexpectedly.
    pause
)
