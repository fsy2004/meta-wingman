# -*- coding: utf-8 -*-
"""
Meta Wingman 环境体检 —— 检测 Python / R 及各自所需的包是否就绪。
既可命令行直接跑(python setup/env_check.py),也被后端 /api/envcheck 调用喂给界面环境面板。
只检测、不安装;安装交给 setup/install.ps1 或界面「一键装」按钮。
"""
from __future__ import annotations
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 后端(轻)所需 Python 包
PY_PKGS = ["fastapi", "uvicorn", "psutil"]
# 10 个 meta 方法所需 R 包(工具包依赖)
R_PKGS = ["metafor", "meta", "netmeta", "mada", "bayesmeta", "robvis",
          "metasens", "estmeansd", "pdftools", "gridExtra", "ggplot2"]


def _find_r() -> str | None:
    for exe in ("Rscript", "Rscript.exe"):
        p = shutil.which(exe)
        if p:
            return p
    # PATH 里没有时再扫常见安装位置(含 winget 用户级、非 C 盘)
    bases = [r"C:\Program Files\R", r"C:\Program Files (x86)\R", r"D:\R", r"D:\Program Files\R"]
    la = os.environ.get("LOCALAPPDATA")
    if la:
        bases.append(str(Path(la) / "Programs" / "R"))
    for base in bases:
        bp = Path(base)
        if bp.exists():
            cands = sorted(bp.glob("**/bin/Rscript.exe"), reverse=True)   # 多版本取最新
            if cands:
                return str(cands[0])
    return None


def check_python() -> dict:
    v = sys.version_info
    pkgs = {p: importlib.util.find_spec(p) is not None for p in PY_PKGS}
    return {
        "present": True,
        "version": f"{v.major}.{v.minor}.{v.micro}",
        "version_ok": (v.major, v.minor) >= (3, 9),
        "packages": pkgs,
        "missing": [p for p, ok in pkgs.items() if not ok],
    }


def check_r() -> dict:
    rscript = _find_r()
    if not rscript:
        return {"present": False, "rscript": None, "version": None,
                "packages": {p: False for p in R_PKGS}, "missing": R_PKGS[:]}
    try:
        ver = subprocess.run([rscript, "--version"], capture_output=True, text=True, timeout=30)
        vtxt = (ver.stdout or ver.stderr or "").splitlines()[0].strip()
    except Exception:
        vtxt = "unknown"
    # 一次性问 R:哪些包缺
    rcode = ("ip<-rownames(installed.packages()); "
             "need<-c(%s); cat(paste(need[!need %%in%% ip], collapse=','))"
             % ",".join(f'\"{p}\"' for p in R_PKGS))
    try:
        out = subprocess.run([rscript, "-e", rcode], capture_output=True, text=True, timeout=120)
        missing = [m for m in (out.stdout.strip().split(",") if out.stdout.strip() else []) if m]
    except Exception:
        missing = R_PKGS[:]
    return {
        "present": True, "rscript": rscript, "version": vtxt,
        "packages": {p: (p not in missing) for p in R_PKGS},
        "missing": missing,
    }


def check() -> dict:
    py = check_python()
    r = check_r()
    ready = (py["version_ok"] and not py["missing"] and r["present"] and not r["missing"])
    return {"ready": ready, "python": py, "r": r}


def _print(rep: dict):
    def line(name, ok, extra=""):
        print(f"  {'✅' if ok else '❌'} {name:22} {extra}")
    print("=" * 58 + "\nMeta Wingman 环境体检\n" + "=" * 58)
    py, r = rep["python"], rep["r"]
    line("Python", py["version_ok"], f"{py['version']}")
    for p, ok in py["packages"].items():
        line(f"  py: {p}", ok)
    line("R (Rscript)", r["present"], r["version"] or "未找到")
    for p, ok in r["packages"].items():
        line(f"  R: {p}", ok)
    print("-" * 58)
    print("  " + ("🟢 全部就绪,可直接运行 Meta Wingman。"
                  if rep["ready"] else
                  "🟡 有缺失。运行 setup/install.ps1 或界面「一键装」补齐(见下)。"))
    if py["missing"]:
        print("  缺 Python 包:", ", ".join(py["missing"]))
    if not r["present"]:
        print("  ❗ 未检测到 R,请先安装 R 4.x(https://cran.r-project.org 或 winget install RProject.R)")
    elif r["missing"]:
        print("  缺 R 包:", ", ".join(r["missing"]))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    rep = check()
    _print(rep)
    if "--json" in sys.argv:
        print(json.dumps(rep, ensure_ascii=False))
