@echo off
title Meta Wingman installer
echo ==================================================
echo   Meta Wingman  -  one-click installer (from Gitee)
echo ==================================================
echo.

if exist "setup\install.ps1" ( echo Detected app folder, installing dependencies... & goto deps )

where git >nul 2>nul
if errorlevel 1 goto zip

echo [1/2] Cloning Meta Wingman from Gitee (git) ...
git clone https://gitee.com/fsy2004/meta-wingman.git
if errorlevel 1 goto zip
goto entered

:zip
echo [1/2] Downloading Meta Wingman zip from Gitee ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try{ Invoke-WebRequest 'https://gitee.com/fsy2004/meta-wingman/repository/archive/master.zip' -OutFile 'mw.zip' -UseBasicParsing; Expand-Archive -Force 'mw.zip' 'mw_tmp'; $d=@(Get-ChildItem 'mw_tmp' -Directory)[0]; if(Test-Path 'meta-wingman'){Remove-Item 'meta-wingman' -Recurse -Force}; Move-Item $d.FullName 'meta-wingman'; Remove-Item 'mw.zip','mw_tmp' -Recurse -Force }catch{ Write-Host $_; exit 1 }"
if errorlevel 1 ( echo Download failed. Check your network, or download manually from https://gitee.com/fsy2004/meta-wingman & pause & exit /b 1 )

:entered
cd meta-wingman

:deps
echo.
echo [2/2] Installing R / Python dependencies (Tsinghua mirror by default) ...
powershell -NoProfile -ExecutionPolicy Bypass -File "setup\install.ps1"
echo.
echo ==================================================
echo   Done!  Double-click  start.bat  to launch Meta Wingman.
echo ==================================================
pause
