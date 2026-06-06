@echo off
chcp 65001 >nul
cd /d %~dp0
title Google Cloud Login

echo ============================================
echo    Google Cloud Login (run once per PC)
echo ============================================
echo.
echo A browser will open. Sign in with your Google
echo account and click Allow.
echo.
echo Press any key to open the browser...
pause >nul

gcloud auth application-default login
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] gcloud command failed.
    echo Install Google Cloud CLI from:
    echo   https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo.
set /p PID="Enter your Google Cloud Project ID (e.g. my-project-123456): "
if "%PID%"=="" (
    echo [ERROR] Project ID cannot be empty. Please run AUTH.bat again.
    pause
    exit /b 1
)

echo.
echo Setting quota project...
gcloud auth application-default set-quota-project %PID%

echo.
echo Enabling Vertex AI API...
gcloud services enable aiplatform.googleapis.com --project=%PID%

echo.
echo ============================================
echo  [OK] Login complete!
echo  You can now run RUN.bat to start the app.
echo ============================================
pause
