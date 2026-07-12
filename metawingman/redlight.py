# -*- coding: utf-8 -*-
"""内存红绿灯:复用 backend/doctor.py(经 paths.py 加入 sys.path)。纯参数方法返回 None。"""
from __future__ import annotations


def estimate(manifest: dict, data_path):
    if not data_path:
        return None
    try:
        import doctor  # backend/doctor.py
        dp = doctor.data_profile(data_path)
        est = doctor.estimate_peak(manifest["mem_hint"], dp)
        rl = doctor.redlight(est["predicted_peak_bytes"])
        return {
            "level": rl.get("level", "green"),
            "peak_gb": est.get("predicted_peak_gb", 0),
            "avail_gb": rl.get("available_gb", 0),
            "n_rows": dp.get("n_rows"), "n_cols": dp.get("n_cols"),
        }
    except Exception:
        return None
