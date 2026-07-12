@echo off
chcp 65001 >nul
title Meta Wingman
cd /d "%~dp0"

REM 启动 Meta Wingman:在本机起 FastAPI 后端,再用系统浏览器打开界面。
REM 需已装好 Python 后端依赖(先跑一次 install.bat)。

where python >nul 2>nul || ( echo [错误] 未检测到 Python。请先运行 install.bat,或安装 Python 3.9+。 & pause & exit /b 1 )

echo 正在启动 Meta Wingman 后端 ...
start "Meta Wingman 后端(请勿关闭此窗口)" /min cmd /c "python -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000"

echo 正在等待后端就绪 ...
powershell -NoProfile -Command "for($i=0;$i -lt 30;$i++){ try{ $null=Invoke-WebRequest 'http://127.0.0.1:8000/api/health' -TimeoutSec 1 -UseBasicParsing; break }catch{ Start-Sleep -Milliseconds 500 } }"

start "" http://127.0.0.1:8000
echo.
echo Meta Wingman 已运行在  http://127.0.0.1:8000 (已打开浏览器)。
echo 要停止:关闭那个最小化的「Meta Wingman 后端」窗口。
echo (本窗口可以关闭。)
timeout /t 6 >nul
