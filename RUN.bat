@echo off
chcp 65001 >nul
cd /d %~dp0
title MV Generator Launcher

echo ============================================
echo    MV Generator - Music Video Maker
echo ============================================
echo.

REM --- Check required programs ---
echo [Check] Verifying installed programs...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found.
    echo Install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js not found.
    echo Install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
where ffmpeg >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARN] FFmpeg not found. Video export may fail.
    echo Install from https://ffmpeg.org/download.html
)
where gcloud >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARN] gcloud not found. Run AUTH.bat first.
)
echo [OK] Checks done.
echo.

REM --- Install backend deps (first run or when requirements change) ---
echo [1/3] Installing backend packages...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt -q
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Backend install failed. Check your internet connection.
    pause
    exit /b 1
)
cd /d "%~dp0"

REM --- Install frontend deps only if node_modules missing ---
echo [2/3] Checking frontend packages...
if not exist "%~dp0frontend\node_modules" (
    echo Installing frontend packages (first run - may take a few minutes)...
    cd /d "%~dp0frontend"
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Frontend install failed. Check Node.js version.
        pause
        exit /b 1
    )
    cd /d "%~dp0"
) else (
    echo [OK] Frontend packages already installed.
)
echo.

REM --- Launch backend in new window ---
echo [3/3] Starting servers...
start "MV-Backend" cmd /k "chcp 65001 >nul && cd /d "%~dp0backend" && python -m uvicorn main:app --port 8000"
echo [OK] Backend starting on port 8000...
timeout /t 6 >nul

REM --- Launch frontend in new window ---
start "MV-Frontend" cmd /k "chcp 65001 >nul && cd /d "%~dp0frontend" && call npm run dev"
echo [OK] Frontend starting on port 5173...
timeout /t 8 >nul

REM --- Open browser ---
start http://localhost:5173

echo.
echo ============================================
echo  App is running at http://localhost:5173
echo  Keep the MV-Backend and MV-Frontend
echo  windows open while using the app.
echo.
echo  To stop: run STOP.bat or close those windows.
echo ============================================
echo.
echo Press any key to close this launcher window.
pause >nul
