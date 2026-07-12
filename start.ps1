# Meta Wingman 启动器(中文界面在 PowerShell 下可靠处理 UTF-8)。由 start.bat 调用。
Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host ""
  Write-Host "[错误] 未找到 Python。请先运行 install.bat 安装环境,或安装 Python 3.9 及以上。" -ForegroundColor Red
  Read-Host "按回车键退出"
  exit 1
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Meta Wingman 正在启动..." -ForegroundColor Cyan
Write-Host "  就绪后会自动打开浏览器: http://127.0.0.1:8000"
Write-Host "  停止运行: 关闭本窗口即可"
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# 后台等后端就绪后自动打开浏览器(不阻塞;后端在本窗口前台运行,日志可见)
$poll = 'for($i=0;$i -lt 60;$i++){try{$null=Invoke-WebRequest ''http://127.0.0.1:8000/api/health'' -TimeoutSec 1 -UseBasicParsing; Start-Process ''http://127.0.0.1:8000''; break}catch{Start-Sleep -Milliseconds 500}}'
Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile', '-Command', $poll

python -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000

Write-Host ""
Write-Host "Meta Wingman 已停止。"
Read-Host "按回车键退出"
