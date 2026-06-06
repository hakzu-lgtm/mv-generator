@echo off
chcp 65001 > nul
echo ===================================
echo  MV Generator - 설치
echo ===================================
echo.

set ROOT=%~dp0

echo [1/2] Python 패키지 설치 중...
cd /d "%ROOT%backend"
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo [오류] pip install 실패.
    echo Python 3.10 이상이 설치되어 있는지 확인하세요.
    echo 설치: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/2] Node.js 패키지 설치 중...
cd /d "%ROOT%frontend"
npm install
if %ERRORLEVEL% neq 0 (
    echo.
    echo [오류] npm install 실패.
    echo Node.js 18 이상이 설치되어 있는지 확인하세요.
    echo 설치: https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo ===================================
echo  설치 완료!
echo.
echo  다음 순서로 실행하세요:
echo    1. auth.bat  (Google 계정 로그인 - 처음 한 번)
echo    2. start.bat (앱 실행)
echo ===================================
pause
