# -*- coding: utf-8 -*-
"""结果区:工具栏(另存 PNG/矢量 PDF、复制表格、打开目录)+ 每个产物一个 tab(图=Pillow,表=Treeview)。
矢量 PDF 已由 R 端生成于同目录,导出=文件拷贝,几乎免费。"""
from __future__ import annotations
import csv
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog

from PIL import Image, ImageTk

from .i18n import I18N


class ResultsView(ttk.Frame):
    def __init__(self, master, on_open_folder=None):
        super().__init__(master)
        self._imgs = []
        self._tab_path = {}
        self.outdir = None
        self._on_open_folder = on_open_folder

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(2, 4))
        self.btn_png = ttk.Button(bar, style="Toolbutton", command=self._save_png)
        self.btn_pdf = ttk.Button(bar, style="Toolbutton", command=self._save_pdf)
        self.btn_copy = ttk.Button(bar, style="Toolbutton", command=self._copy_table)
        self.btn_repro = ttk.Button(bar, style="Toolbutton", command=self._save_repro)
        self.btn_open = ttk.Button(bar, style="Toolbutton", command=self._open)
        for b in (self.btn_png, self.btn_pdf, self.btn_copy, self.btn_repro, self.btn_open):
            b.pack(side="left", padx=(0, 6))

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self._sync())
        self.retitle()
        self._sync()

    def retitle(self):
        self.btn_png.config(text=I18N.t("save_as") + " " + I18N.t("export_png"))
        self.btn_pdf.config(text=I18N.t("save_as") + " " + I18N.t("export_pdf"))
        self.btn_copy.config(text=I18N.t("copy_table"))
        self.btn_repro.config(text=I18N.t("export_script"))
        self.btn_open.config(text=I18N.t("open_folder"))

    def clear(self):
        for t in list(self.nb.tabs()):
            self.nb.forget(t)
        self._imgs.clear()
        self._tab_path.clear()
        self._sync()

    def show(self, outputs, outdir=None):
        self.clear()
        self.outdir = outdir
        for o in outputs:
            if o.lower().endswith(".png"):
                self._image_tab(o)
        for o in outputs:
            if o.lower().endswith(".csv"):
                self._table_tab(o)
        self._sync()

    # ---- 工具栏 ----
    def _cur_path(self):
        return self._tab_path.get(self.nb.select())

    def _pdf_for(self, png):
        if not png:
            return None
        pdf = png[:-4] + ".pdf"
        return pdf if os.path.exists(pdf) else None

    def _sync(self):
        p = self._cur_path()
        is_img = bool(p and p.lower().endswith(".png"))
        is_tbl = bool(p and p.lower().endswith(".csv"))
        self.btn_png.config(state="normal" if is_img else "disabled")
        self.btn_pdf.config(state="normal" if (is_img and self._pdf_for(p)) else "disabled")
        self.btn_copy.config(state="normal" if is_tbl else "disabled")
        has_repro = bool(self.outdir and os.path.exists(os.path.join(self.outdir, "reproduce.R")))
        self.btn_repro.config(state="normal" if has_repro else "disabled")
        self.btn_open.config(state="normal" if self.outdir else "disabled")

    def _save_png(self):
        p = self._cur_path()
        if not p:
            return
        dst = filedialog.asksaveasfilename(defaultextension=".png",
                                           initialfile=os.path.basename(p), filetypes=[("PNG", "*.png")])
        if dst:
            shutil.copyfile(p, dst)

    def _save_pdf(self):
        p = self._pdf_for(self._cur_path())
        if not p:
            return
        dst = filedialog.asksaveasfilename(defaultextension=".pdf",
                                           initialfile=os.path.basename(p), filetypes=[("PDF", "*.pdf")])
        if dst:
            shutil.copyfile(p, dst)

    def _copy_table(self):
        p = self._cur_path()
        if not p or not p.lower().endswith(".csv"):
            return
        try:
            with open(p, encoding="utf-8-sig", newline="") as f:
                rows = list(csv.reader(f))
            self.clipboard_clear()
            self.clipboard_append("\n".join("\t".join(r) for r in rows))
        except Exception:
            pass

    def _save_repro(self):
        from tkinter import messagebox
        if not self.outdir:
            return
        src_r = os.path.join(self.outdir, "reproduce.R")
        if not os.path.exists(src_r):
            return
        dst = filedialog.askdirectory(title=I18N.t("export_script"))
        if not dst:
            return
        try:
            shutil.copyfile(src_r, os.path.join(dst, "reproduce.R"))
            src_d = os.path.join(self.outdir, "data.csv")
            if os.path.exists(src_d):
                shutil.copyfile(src_d, os.path.join(dst, "data.csv"))
            messagebox.showinfo("Meta Wingman", I18N.t("repro_done", d=dst))
        except Exception:
            pass

    def _open(self):
        if self._on_open_folder:
            self._on_open_folder()

    # ---- tabs ----
    def _image_tab(self, path):
        frame = ttk.Frame(self.nb)
        try:
            im = Image.open(path)
            im.thumbnail((960, 660))
            ph = ImageTk.PhotoImage(im)
            self._imgs.append(ph)
            ttk.Label(frame, image=ph).pack(padx=8, pady=8)
        except Exception as e:
            ttk.Label(frame, text=f"(cannot display {os.path.basename(path)}: {e})").pack(padx=8, pady=8)
        self.nb.add(frame, text=os.path.basename(path))
        self._tab_path[str(frame)] = path

    def _table_tab(self, path):
        frame = ttk.Frame(self.nb)
        tree = ttk.Treeview(frame, show="headings", height=13)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
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
            ttk.Label(frame, text=f"(cannot read: {e})").pack(padx=8, pady=8)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.nb.add(frame, text=os.path.basename(path))
        self._tab_path[str(frame)] = path
