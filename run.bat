@echo off
rem Demo / run script: create venv if missing, then launch the pet.
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
    echo Virtual environment not found, running setup.bat first...
    call setup.bat
    if errorlevel 1 exit /b 1
)

.venv\Scripts\python main.py
