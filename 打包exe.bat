@echo off
rem 一键打包成 exe（onedir 便携式）。需已安装运行依赖（先跑 setup.bat）。
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
    echo [ERROR] 未找到 .venv，请先运行 setup.bat。
    pause
    exit /b 1
)

echo 安装打包工具 PyInstaller...
.venv\Scripts\python -m pip install -r requirements-dev.txt
if errorlevel 1 (
    echo [ERROR] PyInstaller 安装失败。
    pause
    exit /b 1
)

echo.
echo 开始打包（首次较慢，约 3~10 分钟）...
.venv\Scripts\python scripts\build_exe.py
pause
