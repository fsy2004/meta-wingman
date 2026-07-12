# -*- coding: utf-8 -*-
"""
FastAPI 网页层 —— 把领域无关内核(doctor + runner)暴露成 HTTP 接口。
UI 只认这些接口, 不感知 R/Python。meta 分析模块与生信模块走同一套接口。

启动:  python -m uvicorn app:app --port 8000   (cwd=backend)
"""
from __future__ import annotations
import json
import subprocess
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

import doctor
import runner
import psutil

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def _resolve(p):
    """相对路径按本产品根目录解析→可下载到任意位置运行;绝对路径原样。"""
    pp = Path(p)
    return pp if pp.is_absolute() else (ROOT / pp).resolve()


LIB = _resolve(CFG["module_library"])                   # 默认库
LIBRARIES = {k: _resolve(v) for k, v in CFG.get("libraries", {}).items()}
MANIFESTS = ROOT / CFG["manifests_dir"]
RUNS = ROOT / CFG["runs_dir"]
CONFIG_DIR = ROOT / "config"
# /api/file 只回传:运行产物(runs/)+ 各适配器的示例数据目录。绝不暴露整个项目树。
_FILE_ALLOWED = [RUNS.resolve()] + sorted({p.resolve() for p in ROOT.glob("adapters/*/example_data") if p.is_dir()})


def _load_cfg_json(name: str, default):
    """读 config/<name>;缺失或损坏则返回 default(不让配置问题打挂接口)。"""
    try:
        return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))
    except Exception:
        return default


def lib_root(manifest: dict) -> Path:
    """按 manifest 的 library 字段解析所属库根目录(默认生信库)。"""
    key = manifest.get("library", "bioinfo")
    return LIB if key == "bioinfo" else LIBRARIES[key]


def _within(p: Path, base: Path) -> bool:
    """p 是否在 base 目录内(精确目录边界;兼容 Python 3.6+,不用 3.9 的 is_relative_to)。"""
    return p == base or base in p.parents


def run_env() -> dict:
    """给 R/Python 子进程追加的环境变量(meta 适配脚本靠 META_TOOLKIT 找工具包)。"""
    e = {}
    if "meta_toolkit" in LIBRARIES:
        e["META_TOOLKIT"] = str(LIBRARIES["meta_toolkit"])
    return e

app = FastAPI(title="Meta Wingman API")
# ★收紧 CORS 到本机来源:避免用户开着本应用时,任意恶意网页跨域驱动 /api/run 执行 R 或 /api/file 读文件
_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000", "http://localhost:8000",   # 后端同端口托管前端
    "http://127.0.0.1:5173", "http://localhost:5173",   # vite 开发态
    "tauri://localhost", "https://tauri.localhost",      # Tauri 桌面壳
]
app.add_middleware(CORSMiddleware, allow_origins=_ALLOWED_ORIGINS, allow_methods=["*"], allow_headers=["*"])


def load_manifest(mid: str) -> dict:
    f = MANIFESTS / f"{mid}.json"
    if not f.exists():
        raise HTTPException(404, f"未找到方法 manifest: {mid}")
    return json.loads(f.read_text(encoding="utf-8"))


def resolve_inputs(manifest: dict, given: dict | None) -> dict:
    """给定 {name: path};缺省用模块自带 example_data。"""
    given = given or {}
    root = lib_root(manifest)
    out = {}
    for spec in manifest.get("inputs", []):
        name = spec["name"]
        path = given.get(name)
        if not path and spec.get("example"):
            path = str(root / manifest["workdir"] / spec["example"])
        if path:
            out[name] = path
    return out


# ------------------------------------------------------------------ 接口
@app.get("/api/machine")
def api_machine():
    return doctor.machine_profile()


@app.get("/api/methods")
def api_methods():
    out = []
    for f in sorted(MANIFESTS.glob("*.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        out.append({k: m.get(k) for k in
                    ("id", "title", "title_en", "family", "category", "language", "tier", "status", "description")})
    return out


@app.get("/api/methods/{mid}")
def api_method(mid: str):
    return load_manifest(mid)


class ProfileReq(BaseModel):
    method_id: str
    path: Optional[str] = None   # 主输入路径;不给则用 example(Optional 兼容 Python 3.9)


@app.post("/api/dataprofile")
def api_dataprofile(req: ProfileReq):
    m = load_manifest(req.method_id)
    inputs = m.get("inputs") or []
    primary = next((s for s in inputs if s.get("primary")), inputs[0] if inputs else None)
    if req.path:
        path = req.path
    elif primary and primary.get("example"):
        path = str(lib_root(m) / m["workdir"] / primary["example"])
    else:  # 无输入/无示例的方法(纯参数型)→ 返回安全的绿灯占位,不裸索引崩 500
        avail = round(psutil.virtual_memory().available / (1024 ** 3), 2)
        return {"data_profile": {"note": "该方法无默认示例数据"},
                "estimate": {"predicted_peak_gb": 0, "detail": "", "killer_dim": "", "calibrated": True},
                "redlight": {"level": "green", "ratio": 0, "predicted_peak_gb": 0, "available_gb": avail,
                             "advice": "该方法以参数为输入,无需数据体检。", "disclaimer": ""}}
    dp = doctor.data_profile(path)
    est = doctor.estimate_peak(m["mem_hint"], dp)
    rl = doctor.redlight(est["predicted_peak_bytes"])
    return {"data_profile": dp, "estimate": est, "redlight": rl}


class RunReq(BaseModel):
    method_id: str
    inputs: Optional[dict] = None
    params: Optional[dict] = None


@app.post("/api/run")
def api_run(req: RunReq):
    m = load_manifest(req.method_id)
    root = lib_root(m)
    inputs = resolve_inputs(m, req.inputs)
    outdir = RUNS / f"{req.method_id}_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    cwd = root / m["workdir"]
    argv = runner.build_argv(m, root, inputs, req.params or {}, outdir)
    limit = int(psutil.virtual_memory().available * 0.9)
    globs = [o["glob"] for o in m["outputs"]]

    def stream():
        for ev in runner.iter_run(argv, cwd, globs, outdir, mem_limit_bytes=limit, extra_env=run_env()):
            yield json.dumps(ev, ensure_ascii=False) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.get("/api/file")
def api_file(path: str):
    """安全地回传产物图/输入文件(仅限 runs 目录与模块库内)。"""
    p = Path(path).resolve()
    if not p.exists():
        raise HTTPException(404, "文件不存在")
    # ★用精确目录边界判断,避免 startswith 被同级兄弟目录(如 ..-private)绕过
    if not any(_within(p, a) for a in _FILE_ALLOWED):
        raise HTTPException(403, "路径不允许")
    return FileResponse(p)


@app.get("/api/health")
def api_health():
    return {"ok": True, "product": CFG.get("product", "launcher"),
            "module_library": str(LIB), "n_methods": len(list(MANIFESTS.glob("*.json")))}


@app.get("/api/envcheck")
def api_envcheck():
    """环境体检:Python / R / 各自的包是否就绪,供界面环境面板显示。"""
    import sys as _sys
    setup_dir = str(ROOT / "setup")
    if setup_dir not in _sys.path:
        _sys.path.insert(0, setup_dir)
    import env_check
    return env_check.check()


@app.get("/api/sources")
def api_sources():
    """镜像源注册表 + 版本门槛,供界面下拉与「版本过低」提示。默认清华 + Gitee。"""
    src = _load_cfg_json("sources.json", {"pip_cran": [], "app_download": []})
    req = _load_cfg_json("requirements.json", {})
    return {
        "pip_cran": src.get("pip_cran", []),
        "pip_cran_default": src.get("pip_cran_default", "tsinghua"),
        "app_download": src.get("app_download", []),
        "app_download_default": src.get("app_download_default", "gitee"),
        "requirements": {"python_min": req.get("python_min", "3.9"),
                         "r_min": req.get("r_min", "4.0")},
    }


class EnvInstallReq(BaseModel):
    source: Optional[str] = None            # pip_cran 注册表里的 id(如 tsinghua/ustc/aliyun/official)


def _resolve_source(sid: Optional[str]) -> dict:
    """把前端传来的源 id 映射成可信 URL(只认注册表内条目,绝不用前端传入的任意 URL→防命令注入)。"""
    src = _load_cfg_json("sources.json", {})
    entries = src.get("pip_cran", [])
    default_id = src.get("pip_cran_default", "tsinghua")
    chosen = next((e for e in entries if e.get("id") == sid), None) \
        or next((e for e in entries if e.get("id") == default_id), None) \
        or (entries[0] if entries else {})
    return chosen


@app.post("/api/envinstall")
def api_envinstall(req: EnvInstallReq = EnvInstallReq()):
    """一键安装缺失依赖:后台跑 setup/install.ps1(用所选镜像源),流式回显日志到界面。"""
    script = ROOT / "setup" / "install.ps1"
    src = _resolve_source(req.source)
    argv = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    if src.get("pip_index"):
        argv += ["-PipIndex", src["pip_index"],
                 "-PipTrustedHost", src.get("pip_trusted_host", ""),
                 "-CranRepo", src.get("cran_repo", "")]

    def stream():
        proc = subprocess.Popen(argv, cwd=str(ROOT), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace", bufsize=1)
        used = src.get("label") or src.get("id") or "默认源"
        yield json.dumps({"type": "log", "line": f"使用镜像源:{used}"}, ensure_ascii=False) + "\n"
        try:
            for line in proc.stdout:
                yield json.dumps({"type": "log", "line": line.rstrip("\n")}, ensure_ascii=False) + "\n"
            proc.wait()
            yield json.dumps({"type": "done", "returncode": proc.returncode}, ensure_ascii=False) + "\n"
        finally:
            if proc.poll() is None:                 # 前端断开→别留孤儿安装进程
                runner._kill_tree(proc)

    return StreamingResponse(stream(), media_type="application/x-ndjson")


# ---- 生产:后端在同端口托管已构建的前端(frontend/dist),终端用户无需 Node ----
# 必须放在所有 /api 路由之后:mount("/") 只兜底未匹配路径,不影响 API。
_dist = ROOT / "frontend" / "dist"
if _dist.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="frontend")
