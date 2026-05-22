@echo off
REM Setup script for Nova Learning Assistant (Windows)
REM Creates conda environments and installs dependencies

setlocal enabledelayedexpansion

echo.
echo ======================================
echo   Nova Learning Assistant Setup
echo ======================================
echo.

REM Check if conda is installed
conda --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Conda is not installed or not in PATH.
    echo Please install Anaconda or Miniconda from https://www.anaconda.com/download
    pause
    exit /b 1
)

REM Setup Backend
echo [1/4] Setting up backend environment...
set BACKEND_ENV=nova-backend

conda env list | findstr /R "^%BACKEND_ENV%" >nul 2>&1
if errorlevel 1 (
    echo Creating conda environment: %BACKEND_ENV%
    call conda create -n %BACKEND_ENV% python=3.10 -y
) else (
    echo Environment '%BACKEND_ENV%' already exists.
)

call conda activate %BACKEND_ENV%
cd nova-backend

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo [WARNING] Please update .env with your Groq API key
)

pip install -e .
echo [OK] Backend environment ready!
cd ..
echo.

REM Setup Frontend
echo [2/4] Setting up frontend environment...
set FRONTEND_ENV=LearningAssistant

conda env list | findstr /R "^%FRONTEND_ENV%" >nul 2>&1
if errorlevel 1 (
    echo Creating conda environment: %FRONTEND_ENV%
    call conda create -n %FRONTEND_ENV% nodejs=20 -y
) else (
    echo Environment '%FRONTEND_ENV%' already exists.
)

call conda activate %FRONTEND_ENV%
cd nova-tutor
call npm install
echo [OK] Frontend environment ready!
cd ..
echo.

echo ======================================
echo   Setup Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Update ./nova-backend/.env with your Groq API key
echo 2. Run: run.bat (to start both backend and frontend)
echo.
echo Quick reference:
echo   Backend environment:  conda activate %BACKEND_ENV%
echo   Frontend environment: conda activate %FRONTEND_ENV%
echo.
pause
