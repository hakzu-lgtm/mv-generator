@echo off
chcp 65001 >nul
cd /d %~dp0
title Install Dependencies

echo ============================================
echo    MV Generator - Install Dependencies
echo ============================================
echo.

echo [1/2] Installing backend packages...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Backend install failed.
    echo Make sure Python 3.10+ is installed: https://www.python.org/downloads/
    pause
    exit /b 1
)
cd /d "%~dp0"

echo.
echo [2/2] Installing frontend packages...
cd /d "%~dp0frontend"
call npm install
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Frontend install failed.
    echo Make sure Node.js 18+ is installed: https://nodejs.org/
    pause
    exit /b 1
)
cd /d "%~dp0"

echo.
echo ============================================
echo  [OK] All packages installed!
echo.
echo  Next steps:
echo    1. Run AUTH.bat  (Google login - first time only)
echo    2. Run RUN.bat   (Launch the app)
echo ============================================
pause
