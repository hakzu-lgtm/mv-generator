@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Install Dependencies

echo ============================================
echo    MV Generator - Install Dependencies
echo ============================================
echo.

echo [1/2] Installing backend packages...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt
if errorlevel 1 echo [ERROR] Backend install failed. Check Python 3.10+ is installed.& pause & exit /b
cd /d "%~dp0"

echo.
echo [2/2] Installing frontend packages...
cd /d "%~dp0frontend"
call npm install
if errorlevel 1 echo [ERROR] Frontend install failed. Check Node.js 18+ is installed.& pause & exit /b
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
