@echo off
chcp 65001 > nul
echo ===================================
echo  Google Cloud 로그인
echo ===================================
echo.
echo 브라우저가 열리면 본인 Google 계정으로 로그인하세요.
echo (학교/개인 구글 계정 모두 가능)
echo.

gcloud auth application-default login
if %ERRORLEVEL% neq 0 (
    echo.
    echo [오류] gcloud 실행 실패.
    echo Google Cloud CLI가 설치되어 있는지 확인하세요.
    echo 설치: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo.
set /p PID="Google Cloud Project ID 입력 (예: my-project-123456): "
if "%PID%"=="" (
    echo Project ID가 비어 있습니다. 다시 실행하세요.
    pause
    exit /b 1
)

echo.
echo 프로젝트 설정 중...
gcloud auth application-default set-quota-project %PID%

echo.
echo Vertex AI API 활성화 중... (처음에만 1~2분 소요)
gcloud services enable aiplatform.googleapis.com --project=%PID%

echo.
echo ===================================
echo  로그인 완료!
echo  이제 start.bat 을 실행하세요.
echo ===================================
pause
