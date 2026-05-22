@echo off
REM Run script for Nova Learning Assistant (Windows)
REM Starts both backend (FastAPI) and frontend (Vite) servers

setlocal enabledelayedexpansion

set BACKEND_ENV=nova-backend
set FRONTEND_ENV=LearningAssistant

echo.
echo ======================================
echo   Starting Nova Learning Assistant
echo ======================================
echo.

REM Check if conda is installed
conda --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Conda is not installed. Please run setup.bat first.
    pause
    exit /b 1
)

REM Check if environments exist
conda env list | findstr /R "^%BACKEND_ENV%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend environment '%BACKEND_ENV%' not found.
    echo Please run: setup.bat
    pause
    exit /b 1
)

conda env list | findstr /R "^%FRONTEND_ENV%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Frontend environment '%FRONTEND_ENV%' not found.
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

echo [INFO] Starting Backend (FastAPI)...
echo        Environment: %BACKEND_ENV%
echo        Directory: ./nova-backend
echo.

REM Start backend in a new window
start "Nova Backend" cmd /k "call conda activate %BACKEND_ENV% && cd nova-backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak

echo [INFO] Starting Frontend (Vite Dev Server)...
echo        Environment: %FRONTEND_ENV%
echo        Directory: ./nova-tutor
echo.

REM Start frontend in a new window
start "Nova Frontend" cmd /k "call conda activate %FRONTEND_ENV% && cd nova-tutor && npm run dev"

echo.
echo ======================================
echo   Nova is Running!
echo ======================================
echo.
echo Access points:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Both servers are running in separate windows.
echo Close each window to stop the servers.
echo.
pause
