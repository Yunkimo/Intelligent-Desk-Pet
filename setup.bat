@echo off
rem One-time environment setup: create venv and install dependencies.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    exit /b 1
)

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

echo Installing dependencies...
.venv\Scripts\python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
echo Done. Next steps:
echo   1. copy .env.example .env  and fill in LLM_API_KEY
echo   2. run  run.bat
