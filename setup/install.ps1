# =====================================================================
# Meta Wingman - transparent, mirror-selectable environment setup.
# 源可由参数传入(前端下拉/命令行);不传则用默认清华。是"哑执行器",只按给定源装。
# 逐段打印:装什么(包+期望)/用什么源(URL)/结果状态。
# 用法:
#   powershell -ExecutionPolicy Bypass -File setup\install.ps1
#   powershell -ExecutionPolicy Bypass -File setup\install.ps1 -PipIndex https://mirrors.aliyun.com/pypi/simple -PipTrustedHost mirrors.aliyun.com -CranRepo https://mirrors.aliyun.com/CRAN
# =====================================================================
param(
  [string]$PipIndex       = "https://pypi.tuna.tsinghua.edu.cn/simple",
  [string]$PipTrustedHost = "pypi.tuna.tsinghua.edu.cn",
  [string]$CranRepo       = "https://mirrors.tuna.tsinghua.edu.cn/CRAN"
)
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
$req  = Get-Content (Join-Path $root "config\requirements.json") -Raw -Encoding UTF8 | ConvertFrom-Json

Write-Host "================ Meta Wingman environment setup ================" -ForegroundColor Cyan
Write-Host ("  install source | pip  = {0}" -f $PipIndex)  -ForegroundColor DarkGray
Write-Host ("  install source | CRAN = {0}" -f $CranRepo)  -ForegroundColor DarkGray
Write-Host ""

# ---- Python(后端,轻)----
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
  Write-Host ("[MISSING] Python not found. Install Python {0}+ first:" -f $req.python_min) -ForegroundColor Yellow
  Write-Host "    winget install Python.Python.3.12    or    https://www.python.org/downloads/"
} else {
  Write-Host ("[OK] Python: {0}" -f (python --version)) -ForegroundColor Green
  Write-Host ("  Plan: pip install  {0}   (source: {1})" -f ($req.python_packages -join ", "), $PipIndex)
  python -m pip install -i $PipIndex --trusted-host $PipTrustedHost @($req.python_packages)
}
Write-Host ""

# ---- R(10+1 方法)----
$r = Get-Command Rscript -ErrorAction SilentlyContinue
if (-not $r) {
  Write-Host ("[MISSING] R not found. Install R {0}+ first:" -f $req.r_min) -ForegroundColor Yellow
  Write-Host "    winget install RProject.R    or    https://mirrors.tuna.tsinghua.edu.cn/CRAN/"
} else {
  Write-Host ("[OK] R: {0}" -f ((Rscript --version 2>&1 | Select-Object -First 1))) -ForegroundColor Green
  Write-Host ("  Plan: install missing of {0} pkgs   (source: {1})" -f $req.r_packages.Count, $CranRepo)
  & Rscript (Join-Path $PSScriptRoot "install_r_packages.R") $CranRepo @($req.r_packages)
}
Write-Host "================ done ================" -ForegroundColor Cyan
Write-Host "Re-check anytime:  python setup\env_check.py"
