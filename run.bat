@echo off
title JARVIS - AI Assistant
cd /d "%~dp0"

echo ==========================================
echo   J.A.R.V.I.S  - Starting up...
echo ==========================================
echo.
echo  Say "Hey Jarvis" or "Wake Jarvis" to activate
echo.

python run.py

if errorlevel 1 (
    echo.
    echo [ERROR] Jarvis crashed. Check above for details.
    pause
)
