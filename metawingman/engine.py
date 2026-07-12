# -*- coding: utf-8 -*-
"""跑一个方法:构 argv、定位 R、注入 META_TOOLKIT、子进程流式输出、墙钟超时、收产物。
UI 无关:后台线程读子进程,主线程(Tk)用 Run.poll() 非阻塞取行。"""
from __future__ import annotations
import json
import os
import queue
import subprocess
import threading
import time
import uuid
from pathlib import Path

from .paths import ROOT, MANIFESTS, TOOLKIT, run_root
from .rlocate import find_rscript

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0   # 不弹子进程黑窗


def list_methods() -> list[dict]:
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(MANIFESTS.glob("*.json"))]


def load_manifest(mid: str) -> dict:
    return json.loads((MANIFESTS / f"{mid}.json").read_text(encoding="utf-8"))


def primary_input(m: dict):
    ins = m.get("inputs", [])
    return next((s for s in ins if s.get("primary")), ins[0] if ins else None)


def example_path(m: dict):
    pin = primary_input(m)
    if pin and pin.get("example"):
        return str(ROOT / m["workdir"] / pin["example"])
    return None


def build_argv(m, rscript, input_path, params, outdir):
    argv = [rscript, str(ROOT / m["entry"])]
    for spec in m.get("inputs", []):
        path = input_path if spec.get("primary") else None
        if not path and spec.get("example"):
            path = str(ROOT / m["workdir"] / spec["example"])
        if path:
            argv += [spec["flag"], str(path)]
    argv += ["--outdir", str(outdir)]
    flags = m.get("param_flags", {})
    for k, v in (params or {}).items():
        if k in flags and v is not None and str(v) != "":
            argv += [flags[k], str(v)]
    return argv


class Run:
    """一次方法运行。start() 起后台线程;UI 反复 poll() 取 (kind, payload):
    kind ∈ {'log','error','done'};done 的 payload 是 returncode。结束后读 .outputs / .returncode。"""

    def __init__(self, m: dict, input_path: str | None = None, params: dict | None = None, timeout: int = 900):
        self.m = m
        self.input_path = input_path
        self.params = params or {}
        self.timeout = timeout
        self.q: queue.Queue = queue.Queue()
        self.outdir = run_root() / f'{m["id"]}_{time.strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:6]}'
        self.proc = None
        self.returncode = None
        self.outputs: list[str] = []
        self._cancelled = False
        self.done = False

    def start(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def cancel(self):
        self._cancelled = True
        if self.proc and self.proc.poll() is None:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                               creationflags=CREATE_NO_WINDOW, capture_output=True)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass

    def _worker(self):
        rscript = find_rscript()
        if not rscript:
            self.q.put(("error", "R (Rscript) not found / 未找到 R。请安装 R,或在设置中指定 Rscript.exe。"))
            self._finish(127)
            return
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
            argv = build_argv(self.m, rscript, self.input_path, self.params, self.outdir)
            env = os.environ.copy()
            env["META_TOOLKIT"] = str(TOOLKIT)
            env["PATH"] = str(Path(rscript).parent) + os.pathsep + env.get("PATH", "")
            self.q.put(("log", "$ " + subprocess.list2cmdline(argv)))
            self.proc = subprocess.Popen(
                argv, cwd=str(ROOT / self.m["workdir"]),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                encoding="utf-8", errors="replace", bufsize=1,
                creationflags=CREATE_NO_WINDOW, env=env,
            )
        except Exception as e:
            self.q.put(("error", f"launch failed / 启动失败: {e}"))
            self._finish(127)
            return

        start = time.monotonic()

        def watchdog():
            while self.proc and self.proc.poll() is None:
                if not self._cancelled and time.monotonic() - start > self.timeout:
                    self.q.put(("error", f"timed out after {self.timeout}s / 超时已终止"))
                    self.cancel()
                    return
                time.sleep(1)

        threading.Thread(target=watchdog, daemon=True).start()
        try:
            for line in self.proc.stdout:
                self.q.put(("log", line.rstrip("\r\n")))
        except Exception:
            pass
        self.proc.wait()
        rc = self.proc.returncode
        for o in self.m.get("outputs", []):
            self.outputs += sorted(str(p) for p in self.outdir.glob(o["glob"]))
        self._finish(rc)

    def _finish(self, rc):
        self.returncode = rc
        self.done = True
        self.q.put(("done", rc))

    def poll(self):
        """非阻塞返回积累的 (kind, payload) 列表。"""
        items = []
        try:
            while True:
                items.append(self.q.get_nowait())
        except queue.Empty:
            pass
        return items
