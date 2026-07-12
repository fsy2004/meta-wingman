# -*- coding: utf-8 -*-
"""
零安装冒烟测试: 不需要 fastapi/npm, 只用已装的 psutil/anndata + Rscript,
端到端验证平台核心链: 机器体检 → 数据规模 → 内存红绿灯 → 子进程跑真实模块 → 出图 + 看门狗。

用法:  python backend/test_core.py 054_wgcna
       python backend/test_core.py 046_scrna
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

try:                                    # Windows 控制台默认 GBK, 强制 UTF-8 避免中文/上标崩溃
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doctor
import runner

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def _resolve(p):
    pp = Path(p)
    return pp if pp.is_absolute() else (ROOT / pp).resolve()


LIB = _resolve(CFG["module_library"])
LIBRARIES = {k: _resolve(v) for k, v in CFG.get("libraries", {}).items()}


def lib_root(m):
    key = m.get("library", "bioinfo")
    return LIB if key == "bioinfo" else LIBRARIES[key]


def run_env():
    return {"META_TOOLKIT": str(LIBRARIES["meta_toolkit"])} if "meta_toolkit" in LIBRARIES else {}


def bar(t): print("\n" + "=" * 64 + f"\n{t}\n" + "=" * 64)


def main():
    mid = sys.argv[1] if len(sys.argv) > 1 else "054_wgcna"
    manifest = json.loads((ROOT / "manifests" / f"{mid}.json").read_text(encoding="utf-8"))
    root = lib_root(manifest)

    bar(f"① 机器体检")
    mp = doctor.machine_profile()
    for k, v in mp.items():
        print(f"  {k:18} {v}")

    bar(f"② 方法: {manifest['title']}  [{manifest['family']} · {manifest['language']} · {manifest['tier']}]")
    primary_spec = next(s for s in manifest["inputs"] if s.get("primary"))
    example = root / manifest["workdir"] / primary_spec["example"]
    print(f"  主输入: {example.name}")
    dp = doctor.data_profile(str(example))
    print(f"  数据规模: {dp.get('n_rows')} 行(基因) × {dp.get('n_cols')} 列  ·  {dp.get('size_mb')} MB")

    bar("③ 临跑前内存红绿灯(估算)")
    est = doctor.estimate_peak(manifest["mem_hint"], dp)
    rl = doctor.redlight(est["predicted_peak_bytes"])
    light = {"green": "🟢 绿", "yellow": "🟡 黄", "red": "🔴 红"}[rl["level"]]
    print(f"  内存杀手维度: {est['killer_dim']}   模型: {est['detail']}")
    print(f"  预估峰值 ≈ {est['predicted_peak_gb']} GB   可用 {rl['available_gb']} GB   占比 {rl['ratio']}")
    print(f"  红绿灯: {light}   {rl['advice']}")
    print(f"  ({rl['disclaimer']})")

    bar("④ 跑真实模块(子进程 + 内存看门狗 + 出图)")
    outdir = ROOT / CFG["runs_dir"] / f"{mid}_smoke"
    cwd = root / manifest["workdir"]
    inputs = {s["name"]: str(root / manifest["workdir"] / s["example"])
              for s in manifest["inputs"] if s.get("example")}
    argv = runner.build_argv(manifest, root, inputs, {}, outdir)
    limit = int(doctor.psutil.virtual_memory().available * 0.9)  # 冒烟用宽松红线
    result = None
    for ev in runner.iter_run(argv, cwd, [o["glob"] for o in manifest["outputs"]], outdir, mem_limit_bytes=limit, extra_env=run_env()):
        if ev["type"] == "log":
            print("  | " + ev["line"])
        elif ev["type"] == "killed":
            print("  ⚠️  看门狗: " + ev["reason"])
        elif ev["type"] == "done":
            result = ev

    bar("⑤ 结果")
    print(f"  返回码: {result['returncode']}   实测峰值内存: {result['peak_gb']} GB")
    print(f"  产物图({len(result['outputs'])}):")
    for o in result["outputs"]:
        print("    - " + Path(o).name)
    ok = result["returncode"] == 0 and result["outputs"]
    print("\n  " + ("✅ 整链跑通" if ok else "❌ 有问题,见上面日志"))


if __name__ == "__main__":
    main()
