@echo off
chcp 65001 >nul
title Meta Wingman 安装器
echo ==================================================
echo   Meta Wingman  ·  一键安装(从 Gitee 拉取)
echo ==================================================
echo.

REM 已经在应用文件夹里?那就只装依赖。
if exist "setup\install.ps1" ( echo 检测到已在应用目录,直接安装依赖... & goto deps )

where git >nul 2>nul
if %errorlevel%==0 (
  echo [1/2] 正在用 git 从 Gitee 克隆 Meta Wingman ...
  git clone https://gitee.com/fsy2004/meta-wingman.git
  if errorlevel 1 goto zip
  goto entered
)

:zip
echo [1/2] 未检测到 git,改为从 Gitee 下载压缩包 ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try{ Invoke-WebRequest 'https://gitee.com/fsy2004/meta-wingman/repository/archive/master.zip' -OutFile 'mw.zip' -UseBasicParsing; Expand-Archive -Force 'mw.zip' 'mw_tmp'; $d=@(Get-ChildItem 'mw_tmp' -Directory)[0]; if(Test-Path 'meta-wingman'){Remove-Item 'meta-wingman' -Recurse -Force}; Move-Item $d.FullName 'meta-wingman'; Remove-Item 'mw.zip','mw_tmp' -Recurse -Force }catch{ Write-Host $_; exit 1 }"
if errorlevel 1 ( echo 下载失败。请检查网络,或手动到 https://gitee.com/fsy2004/meta-wingman 下载。 & pause & exit /b 1 )

:entered
cd meta-wingman

:deps
echo.
echo [2/2] 正在安装 R / Python 依赖(默认清华镜像)...
powershell -NoProfile -ExecutionPolicy Bypass -File "setup\install.ps1"
echo.
echo ==================================================
echo   安装完成!双击  start.bat  即可启动 Meta Wingman。
echo   (它会在本机起后端并用系统浏览器打开界面)
echo ==================================================
pause
