@echo off
title C-Encrypt Secure Cloud Platform
color 0B

echo ===================================================
echo        C-Encrypt Secure Cloud Platform
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python from https://www.python.org/ 
    echo IMPORTANT: Check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Ensure dependencies are installed silently
echo [*] Checking and installing required modules (one-time setup)...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install modules automatically. Trying with --user...
    pip install -q --user -r requirements.txt
)

echo [*] Starting C-Encrypt...
echo.
python main.py

:: Keep window open if the script crashes or exits unexpectedly
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with an error.
    pause
)
