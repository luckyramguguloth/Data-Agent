@echo off
title AI Data Analyst Agent - Stop Services
echo ============================================================
echo         AI DATA ANALYST AGENT - STOPPING SERVICES
echo ============================================================
echo.

echo [INFO] Terminating AI Data Analyst backend and frontend processes...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Process -Name python, streamlit -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*AI DATA AGENT*' } | Stop-Process -Force -ErrorAction SilentlyContinue"

echo.
echo [SUCCESS] AI Data Analyst services have been stopped.
echo.
pause
