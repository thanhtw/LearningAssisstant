@echo off
REM Run frontend only (Vite dev server) - Windows

setlocal enabledelayedexpansion

set FRONTEND_ENV=LearningAssistant

echo.
echo ======================================
echo   Starting Nova Frontend (Vite)
echo ======================================
echo.

REM Check if conda is installed
conda --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Conda is not installed. Please run setup.bat first.
    pause
    exit /b 1
)

REM Check if environment exists
conda env list | findstr /R "^%FRONTEND_ENV%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Frontend environment '%FRONTEND_ENV%' not found.
    echo Please run: setup.bat
    pause
    exit /b 1
)

echo [INFO] Configuration:
echo        Environment: %FRONTEND_ENV%
echo        Directory: ./nova-tutor
echo.

call conda activate %FRONTEND_ENV%
cd nova-tutor

echo [OK] Frontend starting...
echo.
echo Access point:
echo   Frontend: http://localhost:5173
echo.

call npm run dev

pause
