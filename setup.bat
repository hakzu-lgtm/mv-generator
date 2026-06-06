@echo off
chcp 65001 >nul
set ROOT=%~dp0

echo === MV Generator: Install ===
echo.

echo [1/2] Installing Python packages...
cd /d "%ROOT%backend"
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: pip install failed.
    echo Make sure Python 3.10+ is installed: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/2] Installing Node.js packages...
cd /d "%ROOT%frontend"
call npm install
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm install failed.
    echo Make sure Node.js 18+ is installed: https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo === Install complete! ===
echo   1. Run auth.bat  ^(Google login - first time only^)
echo   2. Run start.bat ^(Launch app^)
pause
