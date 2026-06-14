@echo off
REM ============================================================================
REM C-Encrypt EXE Builder
REM ============================================================================
REM This script builds a portable single-file executable for C-Encrypt.
REM 
REM Requirements:
REM   - Python 3.7+
REM   - PyInstaller (pip install pyinstaller)
REM
REM Output:
REM   dist\C-Encrypt.exe (portable, standalone executable)
REM ============================================================================

echo.
echo ============================================================================
echo  C-Encrypt EXE Builder v1.0
echo ============================================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller not found!
    echo.
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller.
        echo Please run: pip install pyinstaller
        pause
        exit /b 1
    )
)

echo [INFO] PyInstaller found
echo.
echo [INFO] Starting build process...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist C-Encrypt.spec del /q C-Encrypt.spec

REM Build the executable with cryptography bundled and icon
python -m PyInstaller --onefile --name C-Encrypt --console --icon=logo.ico --collect-all cryptography main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo  BUILD SUCCESSFUL!
echo ============================================================================
echo.
echo The portable executable has been created:
echo   dist\C-Encrypt.exe
echo.
echo To use:
echo   1. Copy C-Encrypt.exe to any folder
echo   2. Run C-Encrypt.exe
echo   3. cstorage folder will be created automatically
echo.
echo All user data, keys, and logs will be stored beside the EXE.
echo ============================================================================
echo.
echo TESTING INSTRUCTIONS:
echo   1. Create a new empty folder (e.g., Desktop\TestRelease)
echo   2. Copy dist\C-Encrypt.exe to that folder
echo   3. Run C-Encrypt.exe
echo   4. Verify cstorage folder is created automatically
echo   5. Test login, upload, download features
echo.
echo If all tests pass, the release is ready for distribution!
echo ============================================================================
echo.

pause
