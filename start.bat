@echo off
chcp 65001 >nul
title Meta Wingman
cd /d "%~dp0"

where python >nul 2>nul || ( echo [ERROR] Python not found. Run install.bat first, or install Python 3.9+. & pause & exit /b 1 )

echo Starting Meta Wingman backend ...
start "Meta Wingman backend (keep this window open)" /min cmd /c "python -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000"

echo Waiting for backend to be ready ...
powershell -NoProfile -Command "for($i=0;$i -lt 30;$i++){ try{ $null=Invoke-WebRequest 'http://127.0.0.1:8000/api/health' -TimeoutSec 1 -UseBasicParsing; break }catch{ Start-Sleep -Milliseconds 500 } }"

start "" http://127.0.0.1:8000
echo.
echo Meta Wingman is running at  http://127.0.0.1:8000  (browser opened).
echo To STOP: close the minimized "Meta Wingman backend" window.
echo (You can close this window.)
timeout /t 6 >nul
