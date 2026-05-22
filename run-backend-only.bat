@echo off
REM Run backend only (FastAPI server) - Windows

setlocal enabledelayedexpansion

set BACKEND_ENV=nova-backend

echo.
echo ======================================
echo   Starting Nova Backend (FastAPI)
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
conda env list | findstr /R "^%BACKEND_ENV%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend environment '%BACKEND_ENV%' not found.
    echo Please run: setup.bat
    pause
    exit /b 1
)

REM Check if .env exists
if not exist nova-backend\.env (
    echo [ERROR] .env file not found in nova-backend\
    echo Please copy .env.example to .env and update it with your API keys
    pause
    exit /b 1
)

echo [INFO] Configuration:
echo        Environment: %BACKEND_ENV%
echo        Directory: ./nova-backend
echo.

call conda activate %BACKEND_ENV%
cd nova-backend

echo [OK] Backend starting...
echo.
echo Access points:
echo   API Server: http://localhost:8000
echo   API Docs:   http://localhost:8000/docs
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
