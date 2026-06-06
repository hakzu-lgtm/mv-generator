@echo off
chcp 65001 >nul
title Stop Servers

echo Stopping MV Generator servers...
taskkill /FI "WINDOWTITLE eq MV-Backend*" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq MV-Frontend*" /T /F >nul 2>nul
echo [OK] Servers stopped.
timeout /t 2 >nul
