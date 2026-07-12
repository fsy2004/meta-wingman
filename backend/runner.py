# -*- coding: utf-8 -*-
"""
子进程执行器 —— UI 与语言解耦的关键:只按 manifest 拼命令行、起子进程、流式回传日志,
不感知 R / Python。附带运行时 OOM 看门狗(★Windows 无 rlimit → psutil 轮询子进程树 RSS,
超红线 terminate + 落盘已生成结果 + 友好提示)。
"""
from __future__ import annotations
import glob
import json
import os
import subprocess
import threading
import time
from pathlib import Path

import psutil


def load_config(root: Path) -> dict:
    return json.loads((root / "config.json").read_text(encoding="utf-8"))


def build_argv(manifest: dict, lib_root: Path, inputs: dict, params: dict, outdir: Path) -> list[str]:
    """按 manifest 拼命令行: [interp, entry, --input path, --traits path, --outdir dir, --key val ...]"""
    entry = lib_root / manifest["entry"]
    argv = [manifest["interp"], str(entry)]
    for spec in manifest.get("inputs", []):
        name = spec["name"]
        path = inputs.get(name)
        if path is None and spec.get("example"):
            path = str((lib_root / manifest["workdir"] / spec["example"]))
        if path:
            argv += [spec["flag"], str(path)]
    argv += ["--outdir", str(outdir)]
    flags = manifest.get("param_flags", {})
    for key, val in (params or {}).items():
        if key in flags and val is not None and str(val) != "":
            argv += [flags[key], str(val)]
    return argv


def _tree_rss(proc: psutil.Process) -> int:
    """进程 + 所有子进程的 RSS 之和(Rscript 可能派生 R 子进程)。"""
    total = 0
    try:
        procs = [proc] + proc.children(recursive=True)
        for p in procs:
            try:
                total += p.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return total


def iter_run(argv: list[str], cwd: Path, outputs_glob: list[str], outdir: Path,
             mem_limit_bytes: int | None = None, poll_sec: float = 0.5,
             extra_env: dict | None = None):
    """
    生成器,逐条 yield 事件字典:
      {"type":"log","line":str} / {"type":"mem","rss_gb":float,"peak_gb":float}
      {"type":"killed","reason":str} / {"type":"done","returncode":int,"peak_gb":float,"outputs":[...]}
    extra_env: 追加给子进程的环境变量(如 META_TOOLKIT 指向 meta 工具包路径)。
    """
    outdir.mkdir(parents=True, exist_ok=True)
    yield {"type": "log", "line": "$ " + " ".join(argv)}

    env = os.environ.copy()
    if extra_env:
        env.update({k: str(v) for k, v in extra_env.items() if v is not None})
    proc = subprocess.Popen(
        argv, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", bufsize=1, env=env,
    )
    ps = psutil.Process(proc.pid)
    state = {"peak": 0, "killed": False}

    def watchdog():
        while proc.poll() is None:
            rss = _tree_rss(ps)
            if rss > state["peak"]:
                state["peak"] = rss
            if mem_limit_bytes and rss > mem_limit_bytes:
                state["killed"] = True
                try:
                    for c in ps.children(recursive=True):
                        c.terminate()
                    ps.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                return
            time.sleep(poll_sec)

    wd = threading.Thread(target=watchdog, daemon=True)
    wd.start()

    for line in proc.stdout:
        yield {"type": "log", "line": line.rstrip("\n")}
        yield {"type": "mem", "rss_gb": round(_tree_rss(ps) / (1024**3), 2),
               "peak_gb": round(state["peak"] / (1024**3), 2)}
    proc.wait()
    wd.join(timeout=2)

    if state["killed"]:
        yield {"type": "killed",
               "reason": "内存超过红线,已提前终止以防卡死。建议下采样/减少基因/换更大内存机器。"}

    outs = []
    for g in outputs_glob:
        outs += sorted(glob.glob(str(outdir / g)))
    yield {"type": "done", "returncode": proc.returncode,
           "peak_gb": round(state["peak"] / (1024**3), 2), "outputs": outs}
