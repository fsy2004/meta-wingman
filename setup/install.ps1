# =====================================================================
# Meta Wingman - one-click environment setup (China mirrors).
# Detects Python / R and installs the required dependencies.
# Usage:  powershell -ExecutionPolicy Bypass -File setup\install.ps1
# (Messages kept ASCII: Windows PowerShell 5.1 mis-reads UTF-8 .ps1 without BOM.)
# =====================================================================
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$ErrorActionPreference = "Continue"
Write-Host "================ Meta Wingman environment setup ================" -ForegroundColor Cyan

# ---- Python (backend, light) ----
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
  Write-Host "[MISSING] Python not found. Install Python 3.9+ first:" -ForegroundColor Yellow
  Write-Host "    winget install Python.Python.3.12    or    https://www.python.org/downloads/"
} else {
  Write-Host "[OK] Python: $(python --version)" -ForegroundColor Green
  Write-Host "  -> installing backend deps (Tsinghua mirror)..."
  python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn psutil
}

# ---- R (the 10 meta methods) ----
$r = Get-Command Rscript -ErrorAction SilentlyContinue
if (-not $r) {
  Write-Host "[MISSING] R not found. Install R 4.x first:" -ForegroundColor Yellow
  Write-Host "    winget install RProject.R    or    https://mirrors.tuna.tsinghua.edu.cn/CRAN/"
} else {
  Write-Host "[OK] R: $((Rscript --version 2>&1 | Select-Object -First 1))" -ForegroundColor Green
  Write-Host "  -> installing meta-analysis R packages (Tsinghua CRAN, Windows binaries)..."
  & Rscript "$PSScriptRoot\install_r_packages.R"
}

Write-Host "================ done ================" -ForegroundColor Cyan
Write-Host "Re-check anytime:  python setup\env_check.py"
