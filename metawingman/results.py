# -*- coding: utf-8 -*-
"""结果展示:PNG 图(Pillow 缩放适配)+ CSV 表(Treeview)。每个产物一个 tab。"""
from __future__ import annotations
import csv
import os
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


class ResultsView(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        self._imgs = []   # 保持 PhotoImage 引用,否则被 GC 后图消失

    def clear(self):
        for tab in list(self.tabs()):
            self.forget(tab)
        self._imgs.clear()

    def show(self, outputs):
        self.clear()
        imgs = [o for o in outputs if o.lower().endswith(".png")]
        tbls = [o for o in outputs if o.lower().endswith(".csv")]
        for o in imgs:
            self._image_tab(o)
        for o in tbls:
            self._table_tab(o)

    def _image_tab(self, path):
        frame = ttk.Frame(self)
        try:
            im = Image.open(path)
            im.thumbnail((980, 680))
            ph = ImageTk.PhotoImage(im)
            self._imgs.append(ph)
            ttk.Label(frame, image=ph).pack(padx=10, pady=10)
        except Exception as e:
            ttk.Label(frame, text=f"(cannot display {os.path.basename(path)}: {e})").pack(padx=10, pady=10)
        self.add(frame, text=os.path.basename(path))

    def _table_tab(self, path):
        frame = ttk.Frame(self)
        tree = ttk.Treeview(frame, show="headings", height=14)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                rows = list(csv.reader(f))
            if rows:
                cols = rows[0]
                tree["columns"] = list(range(len(cols)))
                for i, c in enumerate(cols):
                    tree.heading(i, text=c)
                    tree.column(i, width=120, anchor="w", stretch=False)
                for r in rows[1:300]:
                    tree.insert("", "end", values=r)
        except Exception as e:
            ttk.Label(frame, text=f"(cannot read {os.path.basename(path)}: {e})").pack(padx=10, pady=10)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.add(frame, text=os.path.basename(path))
