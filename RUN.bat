@echo off
chcp 65001 >nul
cd /d "%~dp0"
title MV Generator Launcher

echo ============================================
echo    MV Generator - Music Video Maker
echo ============================================
echo.

echo [Check] Verifying installed programs...
where python >nul 2>nul
if errorlevel 1 echo [ERROR] Python not found. Install Python first.& pause & exit /b
where node >nul 2>nul
if errorlevel 1 echo [ERROR] Node.js not found. Install Node.js first.& pause & exit /b
where ffmpeg >nul 2>nul
if errorlevel 1 echo [WARN] FFmpeg not found. Video export may fail.
where gcloud >nul 2>nul
if errorlevel 1 echo [WARN] gcloud not found. Run AUTH.bat first.
echo [OK] Checks done.
echo.

echo [1/3] Installing backend packages...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt -q
cd /d "%~dp0"

echo [2/3] Checking frontend packages...
if exist "%~dp0frontend\node_modules" goto FRONT_OK
echo Installing frontend packages...
cd /d "%~dp0frontend"
call npm install
cd /d "%~dp0"
:FRONT_OK
echo [OK] Frontend ready.
echo.

echo [3/3] Starting servers...
start "MV-Backend" cmd /k "chcp 65001 >nul && cd /d "%~dp0backend" && python -m uvicorn main:app --port 8000"
timeout /t 6 >nul
start "MV-Frontend" cmd /k "chcp 65001 >nul && cd /d "%~dp0frontend" && call npm run dev"
timeout /t 8 >nul
start http://localhost:5173

echo.
echo ============================================
echo  Done! Browser will open at localhost:5173
echo  Keep the two black windows open while using.
echo  To stop: run STOP.bat or close those windows.
echo ============================================
echo.
echo Press any key to close this launcher window.
pause >nul
