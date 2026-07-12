# -*- coding: utf-8 -*-
"""验证 OOM 看门狗: 故意把内存红线设得极低, 看子进程是否被提前终止。"""
from __future__ import annotations
import json, sys
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runner

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
LIB = Path(CFG["module_library"])
mid = sys.argv[1] if len(sys.argv) > 1 else "054_wgcna"
LIMIT_GB = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25

m = json.loads((ROOT / "manifests" / f"{mid}.json").read_text(encoding="utf-8"))
cwd = LIB / m["workdir"]
inputs = {s["name"]: str(LIB / m["workdir"] / s["example"]) for s in m["inputs"] if s.get("example")}
argv = runner.build_argv(m, LIB, inputs, {}, ROOT / CFG["runs_dir"] / f"{mid}_wdtest")
print(f"★ 故意设内存红线 = {LIMIT_GB} GB(远低于该模块实际需要), 期望看门狗拦截\n")
killed = False
for ev in runner.iter_run(argv, cwd, [o["glob"] for o in m["outputs"]],
                          ROOT / CFG["runs_dir"] / f"{mid}_wdtest",
                          mem_limit_bytes=int(LIMIT_GB * 1024**3), poll_sec=0.2):
    if ev["type"] == "log": print("  | " + ev["line"])
    elif ev["type"] == "killed": killed = True; print("\n  ⚠️  " + ev["reason"])
    elif ev["type"] == "done":
        print(f"\n  返回码={ev['returncode']}  实测峰值={ev['peak_gb']}GB  产物数={len(ev['outputs'])}")
print("\n  " + ("✅ 看门狗成功拦截超内存运行" if killed else "❌ 未触发拦截(可能模块太快/太省内存,调低红线重试)"))
