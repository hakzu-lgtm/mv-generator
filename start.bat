@echo off
chcp 65001 > nul
set ROOT=%~dp0

echo ===================================
echo  MV Generator 시작
echo ===================================
echo.

echo [1] 백엔드 서버 시작 (포트 8000)...
start "MV-Backend" cmd /k "chcp 65001 && cd /d %ROOT%backend && uvicorn main:app --reload --port 8000"
timeout /t 3 /nobreak > nul

echo [2] 프론트엔드 시작 (포트 5173)...
start "MV-Frontend" cmd /k "chcp 65001 && cd /d %ROOT%frontend && npm run dev"
timeout /t 5 /nobreak > nul

echo [3] 브라우저 열기...
start http://localhost:5173

echo.
echo 백엔드:  http://localhost:8000
echo 앱:      http://localhost:5173
echo.
echo 종료하려면 MV-Backend / MV-Frontend 창을 닫으세요.
