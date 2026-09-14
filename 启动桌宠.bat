@echo off
cd /d "%~dp0"
.venv\Scripts\python.exe main.py
if errorlevel 1 (
    echo.
    echo 桌宠启动失败，请查看上方错误信息。
    pause
)
