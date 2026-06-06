@echo off
chcp 65001 >nul
set ROOT=%~dp0

echo === MV Generator: Start ===
echo.

echo [1] Starting backend (port 8000)...
start "MV-Backend" cmd /k "chcp 65001 >nul && cd /d %ROOT%backend && uvicorn main:app --reload --port 8000"
timeout /t 3 >nul

echo [2] Starting frontend (port 5173)...
start "MV-Frontend" cmd /k "chcp 65001 >nul && cd /d %ROOT%frontend && call npm run dev"
timeout /t 5 >nul

echo [3] Opening browser...
start http://localhost:5173

echo.
echo Backend:  http://localhost:8000
echo App:      http://localhost:5173
echo.
echo To stop: close the MV-Backend and MV-Frontend windows.
