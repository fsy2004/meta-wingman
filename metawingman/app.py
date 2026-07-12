# -*- coding: utf-8 -*-
"""入口:DPI 感知 → tkinter 自检 → sv-ttk 主题 + 微软雅黑字体 → 建主窗 → mainloop。"""
from __future__ import annotations
import sys


def _set_dpi():
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)      # per-monitor(建 Tk 之前)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def _no_tkinter():
    msg = ("This Python has no tkinter. Reinstall Python from python.org (with Tcl/Tk).\n"
           "此 Python 缺少 tkinter,请从 python.org 重装 Python(含 Tcl/Tk)。")
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "Meta Wingman", 0x10)
    except Exception:
        print(msg)
    sys.exit(1)


def main():
    _set_dpi()
    try:
        import tkinter as tk
        import tkinter.font as tkfont
    except Exception:
        _no_tkinter()

    root = tk.Tk()
    root.title("Meta Wingman")

    try:
        import sv_ttk
        sv_ttk.set_theme("light")
    except Exception:
        pass
    try:
        from tkinter import ttk
        from . import theme
        theme.apply(ttk.Style(root))     # 紧凑行高/字号/配色(在 sv-ttk 之后覆盖)
    except Exception:
        pass

    # 全局字体:微软雅黑(Win8+ 自带,中英同族清晰)
    try:
        for fn in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            tkfont.nametofont(fn).configure(family="Microsoft YaHei UI", size=10)
    except Exception:
        pass

    # HiDPI:DPI 感知后 Tk 不自动缩放,按屏幕 DPI 设 scaling
    try:
        root.tk.call("tk", "scaling", root.winfo_fpixels("1i") / 72.0)
    except Exception:
        pass

    from .ui_main import MainWindow
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
