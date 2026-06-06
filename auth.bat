@echo off
chcp 65001 >nul

echo === Google Cloud Login ===
echo.
echo A browser will open. Sign in with your Google account.
echo.

gcloud auth application-default login
if %ERRORLEVEL% neq 0 (
    echo ERROR: gcloud not found.
    echo Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo.
set /p PID="Enter your Google Cloud Project ID (e.g. my-project-123456): "
if "%PID%"=="" (
    echo Project ID is empty. Please run again.
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
echo === Login complete! Run start.bat to launch the app. ===
pause
