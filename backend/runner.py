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
import platform
import shutil
import subprocess
import threading
import time
from pathlib import Path

import psutil


def _kill_tree(ps: "psutil.Process"):
    """尽力杀掉整个子进程树:Windows 用 taskkill /T 连子孙一起杀,避免孤儿进程继续吃内存。"""
    if ps is None:
        return
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(ps.pid)], capture_output=True, timeout=10)
        else:
            for c in ps.children(recursive=True):
                try:
                    c.terminate()
                except psutil.Error:
                    pass
            ps.terminate()
    except Exception:
        pass


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
    if proc is None:
        return 0
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

    # ★解释器缺失预检:否则 Popen 抛异常发生在流已开始之后,前端收不到 done 会一直转圈
    interp = argv[0]
    if shutil.which(interp) is None and not Path(interp).exists():
        yield {"type": "log", "line": f"✗ 找不到可执行程序 '{interp}'。请确认已安装并在 PATH 中(见顶部环境面板,可点「一键安装」)。"}
        yield {"type": "done", "returncode": 127, "peak_gb": 0, "outputs": []}
        return
    try:
        proc = subprocess.Popen(
            argv, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1, env=env,
        )
    except Exception as e:
        yield {"type": "log", "line": f"✗ 子进程启动失败: {e}"}
        yield {"type": "done", "returncode": 127, "peak_gb": 0, "outputs": []}
        return

    try:
        ps = psutil.Process(proc.pid)
    except psutil.Error:          # 进程秒退(如参数错)→ 不让生成器崩,后面照常读剩余输出并 yield done
        ps = None
    state = {"peak": 0, "killed": False}

    def watchdog():
        while proc.poll() is None:
            rss = _tree_rss(ps)
            if rss > state["peak"]:
                state["peak"] = rss
            if mem_limit_bytes and rss > mem_limit_bytes:
                state["killed"] = True
                _kill_tree(ps)
                return
            time.sleep(poll_sec)

    wd = threading.Thread(target=watchdog, daemon=True)
    wd.start()

    try:
        for line in proc.stdout:
            yield {"type": "log", "line": line.rstrip("\n")}
            yield {"type": "mem", "rss_gb": round(_tree_rss(ps) / (1024**3), 2),
                   "peak_gb": round(state["peak"] / (1024**3), 2)}
        proc.wait()
    finally:
        # ★客户端断开(GeneratorExit)或异常都到这:杀掉未结束的子进程树,防孤儿继续吃内存
        if proc.poll() is None:
            _kill_tree(ps)
        wd.join(timeout=2)

    if state["killed"]:
        yield {"type": "killed",
               "reason": "内存超过红线,已提前终止以防卡死。建议下采样 / 减少研究数 / 换更大内存机器。"}

    outs = []
    for g in outputs_glob:
        outs += sorted(glob.glob(str(outdir / g)))
    yield {"type": "done", "returncode": proc.returncode if proc.returncode is not None else -1,
           "peak_gb": round(state["peak"] / (1024**3), 2), "outputs": outs}
