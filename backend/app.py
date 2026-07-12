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
from pathlib import Path

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


def lib_root(manifest: dict) -> Path:
    """按 manifest 的 library 字段解析所属库根目录(默认生信库)。"""
    key = manifest.get("library", "bioinfo")
    return LIB if key == "bioinfo" else LIBRARIES[key]


def run_env() -> dict:
    """给 R/Python 子进程追加的环境变量(meta 适配脚本靠 META_TOOLKIT 找工具包)。"""
    e = {}
    if "meta_toolkit" in LIBRARIES:
        e["META_TOOLKIT"] = str(LIBRARIES["meta_toolkit"])
    return e

app = FastAPI(title="Bioinfo Launcher API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


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
    path: str | None = None   # 主输入路径;不给则用 example


@app.post("/api/dataprofile")
def api_dataprofile(req: ProfileReq):
    m = load_manifest(req.method_id)
    primary = next((s for s in m["inputs"] if s.get("primary")), m["inputs"][0])
    path = req.path or str(lib_root(m) / m["workdir"] / primary["example"])
    dp = doctor.data_profile(path)
    est = doctor.estimate_peak(m["mem_hint"], dp)
    rl = doctor.redlight(est["predicted_peak_bytes"])
    return {"data_profile": dp, "estimate": est, "redlight": rl}


class RunReq(BaseModel):
    method_id: str
    inputs: dict | None = None
    params: dict | None = None


@app.post("/api/run")
def api_run(req: RunReq):
    m = load_manifest(req.method_id)
    root = lib_root(m)
    inputs = resolve_inputs(m, req.inputs)
    outdir = RUNS / f"{req.method_id}_{time.strftime('%Y%m%d_%H%M%S')}"
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
    allowed = [RUNS.resolve(), LIB.resolve()] + [v.resolve() for v in LIBRARIES.values()]
    if not any(str(p).startswith(str(a)) for a in allowed):
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


@app.post("/api/envinstall")
def api_envinstall():
    """一键安装缺失依赖:后台跑 setup/install.ps1,流式回显日志到界面。"""
    script = ROOT / "setup" / "install.ps1"
    argv = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]

    def stream():
        proc = subprocess.Popen(argv, cwd=str(ROOT), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace", bufsize=1)
        for line in proc.stdout:
            yield json.dumps({"type": "log", "line": line.rstrip("\n")}, ensure_ascii=False) + "\n"
        proc.wait()
        yield json.dumps({"type": "done", "returncode": proc.returncode}, ensure_ascii=False) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")
