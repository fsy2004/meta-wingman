# -*- coding: utf-8 -*-
"""主窗口:左=方法列表(按 family 分组),右=方法详情(数据源/红绿灯/参数/运行/日志/结果)。
双语即时切换。简洁三区布局,不做花哨装饰。"""
from __future__ import annotations
import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from . import engine
from .i18n import I18N
from .form import ParamForm
from .results import ResultsView
from .redlight import estimate as mem_estimate
from .rlocate import find_rscript, set_rscript

_LIGHT = {"green": "#2e9e4f", "yellow": "#d99a00", "red": "#c0392b"}


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.methods = engine.list_methods()
        self.sel = None            # 当前 manifest
        self.data_source = tk.StringVar(value="example")
        self.user_file = None
        self.run = None
        self._refreshers = []      # 语言切换时要重贴文案的回调

        root.geometry("1180x760")
        root.minsize(940, 620)
        self._build_top()
        self._build_body()
        self._apply_r_status()
        # 注册语言刷新:重建列表 + 重贴静态文案 + 重渲当前方法
        I18N.bind(self._on_lang)

    # ---------- 顶栏 ----------
    def _build_top(self):
        top = ttk.Frame(self.root, padding=(14, 10))
        top.pack(side="top", fill="x")
        self.lbl_title = ttk.Label(top, text="Meta Wingman", font=("Microsoft YaHei UI", 15, "bold"))
        self.lbl_title.pack(side="left")
        self.lbl_tag = ttk.Label(top, foreground="#888")
        self.lbl_tag.pack(side="left", padx=12)
        self.btn_lang = ttk.Button(top, width=6, command=I18N.toggle)
        self.btn_lang.pack(side="right")
        self.lbl_rstat = ttk.Label(top)
        self.lbl_rstat.pack(side="right", padx=12)
        ttk.Separator(self.root, orient="horizontal").pack(side="top", fill="x")

    # ---------- 主体 ----------
    def _build_body(self):
        body = ttk.Frame(self.root)
        body.pack(side="top", fill="both", expand=True)

        # 左:方法列表
        left = ttk.Frame(body, padding=(8, 8))
        left.pack(side="left", fill="y")
        self.tree = ttk.Treeview(left, show="tree", selectmode="browse")
        self.tree.column("#0", width=260, minwidth=200)
        self.tree.pack(side="left", fill="y", expand=True)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        ttk.Separator(body, orient="vertical").pack(side="left", fill="y")

        # 右:详情
        right = ttk.Frame(body, padding=(16, 12))
        right.pack(side="left", fill="both", expand=True)
        self.lbl_method = ttk.Label(right, font=("Microsoft YaHei UI", 13, "bold"), wraplength=760)
        self.lbl_method.pack(anchor="w")
        self.lbl_desc = ttk.Label(right, foreground="#666", wraplength=760, justify="left")
        self.lbl_desc.pack(anchor="w", pady=(4, 10))

        # 数据源
        self.ds_frame = ttk.LabelFrame(right, padding=(10, 8))
        self.ds_frame.pack(fill="x", pady=6)
        self.rb_ex = ttk.Radiobutton(self.ds_frame, variable=self.data_source, value="example", command=self._on_source)
        self.rb_ex.grid(row=0, column=0, sticky="w", padx=(0, 16))
        self.rb_mine = ttk.Radiobutton(self.ds_frame, variable=self.data_source, value="mine", command=self._on_source)
        self.rb_mine.grid(row=0, column=1, sticky="w")
        self.btn_file = ttk.Button(self.ds_frame, command=self._choose_file)
        self.btn_file.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.lbl_file = ttk.Label(self.ds_frame, foreground="#2e9e4f")
        self.lbl_file.grid(row=1, column=2, sticky="w", padx=10)
        self.lbl_cols = ttk.Label(self.ds_frame, foreground="#888", wraplength=680, justify="left")
        self.lbl_cols.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))

        # 红绿灯
        self.lbl_mem = ttk.Label(right)
        self.lbl_mem.pack(anchor="w", pady=(6, 2))

        # 参数
        self.params_frame = ttk.LabelFrame(right, padding=(10, 8))
        self.params_frame.pack(fill="x", pady=6)
        self.form = None

        # 运行按钮
        rowb = ttk.Frame(right)
        rowb.pack(fill="x", pady=(6, 2))
        self.btn_run = ttk.Button(rowb, style="Accent.TButton", command=self._run)
        self.btn_run.pack(side="left")
        self.btn_cancel = ttk.Button(rowb, command=self._cancel)
        self.btn_open = ttk.Button(rowb, command=self._open_folder)

        # 底部:日志 / 结果
        self.nb = ttk.Notebook(right)
        self.nb.pack(fill="both", expand=True, pady=(8, 0))
        logf = ttk.Frame(self.nb)
        self.log = tk.Text(logf, height=8, wrap="word", font=("Consolas", 9))
        lsb = ttk.Scrollbar(logf, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set, state="disabled")
        self.log.pack(side="left", fill="both", expand=True)
        lsb.pack(side="right", fill="y")
        self.results = ResultsView(self.nb)
        self.nb.add(logf, text="Log")
        self.nb.add(self.results, text="Results")

        self._show_detail(False)

    # ---------- 语言刷新 ----------
    def _on_lang(self):
        self.lbl_tag.config(text=I18N.t("tagline"))
        self.btn_lang.config(text=I18N.t("lang_button"))
        self.rb_ex.config(text=I18N.both("use_example"))
        self.rb_mine.config(text=I18N.both("use_mine"))
        self.btn_file.config(text=I18N.t("choose_file"))
        self.btn_cancel.config(text=I18N.t("cancel"))
        self.btn_open.config(text=I18N.t("open_folder"))
        self.ds_frame.config(text=I18N.t("data"))
        self.params_frame.config(text=I18N.t("parameters"))
        self.nb.tab(0, text=I18N.t("log"))
        self.nb.tab(1, text=I18N.t("results"))
        self._apply_r_status()
        self._rebuild_tree()
        if self.sel:
            self._render_method()
        else:
            self.lbl_method.config(text="🪽 Meta Wingman")
            self.lbl_desc.config(text=I18N.t("select_method"))
        self._update_run_button()

    def _apply_r_status(self):
        ok = bool(find_rscript())
        self.lbl_rstat.config(text=("● " + I18N.t("r_ok")) if ok else ("● " + I18N.t("r_missing")),
                              foreground=_LIGHT["green"] if ok else _LIGHT["red"])

    # ---------- 方法列表 ----------
    def _rebuild_tree(self):
        self.tree.delete(*self.tree.get_children())
        self._node_to_mid = {}
        fams = {}
        for m in self.methods:
            fams.setdefault(m.get("family", "Meta"), []).append(m)
        for fam, items in fams.items():
            parent = self.tree.insert("", "end", text=fam, open=True)
            for m in items:
                node = self.tree.insert(parent, "end", text="  " + I18N.title_of(m))
                self._node_to_mid[node] = m["id"]
        # 重新选中当前
        if self.sel:
            for node, mid in self._node_to_mid.items():
                if mid == self.sel["id"]:
                    self.tree.selection_set(node)
                    break

    def _on_select(self, _evt):
        node = (self.tree.selection() or [None])[0]
        mid = getattr(self, "_node_to_mid", {}).get(node)
        if mid:
            self.pick(mid)

    # ---------- 选方法 ----------
    def pick(self, mid):
        self.sel = engine.load_manifest(mid)
        self.data_source.set("example")
        self.user_file = None
        self._show_detail(True)
        self._render_method()

    def _render_method(self):
        m = self.sel
        self.lbl_method.config(text=I18N.title_of(m))
        self.lbl_desc.config(text=m.get("description", ""))
        pin = engine.primary_input(m)
        spec = (pin or {}).get("spec", "")
        self.lbl_cols.config(text=(I18N.t("columns_needed") + ": " + spec) if spec else "")
        # 参数表单(重建)
        if self.form:
            self.form.destroy()
        self.form = ParamForm(self.params_frame, m.get("params_schema"))
        self.form.pack(fill="x")
        # 清日志/结果
        self._set_log("")
        self.results.clear()
        self._refresh_file_label()
        self._update_redlight()
        self._update_run_button()

    def _on_source(self):
        if self.data_source.get() == "mine" and not self.user_file:
            self._choose_file()
        self._refresh_file_label()
        self._update_redlight()
        self._update_run_button()

    def _choose_file(self):
        path = filedialog.askopenfilename(
            title="CSV", filetypes=[("CSV", "*.csv"), ("Text", "*.txt *.tsv"), ("All", "*.*")])
        if path:
            self.user_file = os.path.normpath(path)
            self.data_source.set("mine")
        self._refresh_file_label()
        self._update_redlight()
        self._update_run_button()

    def _refresh_file_label(self):
        if self.data_source.get() == "mine" and self.user_file:
            self.lbl_file.config(text="✓ " + I18N.t("loaded") + ": " + os.path.basename(self.user_file))
        else:
            self.lbl_file.config(text="")

    def _cur_data_path(self):
        if self.data_source.get() == "mine":
            return self.user_file
        return engine.example_path(self.sel) if self.sel else None

    def _update_redlight(self):
        r = mem_estimate(self.sel, self._cur_data_path()) if self.sel else None
        if not r:
            self.lbl_mem.config(text="")
            return
        dims = f'{r.get("n_rows","?")}×{r.get("n_cols","?")}'
        self.lbl_mem.config(
            text=f'● {I18N.t("memory")}: {dims} · ' + I18N.t("peak_mem", gb=r["peak_gb"], avail=r["avail_gb"]),
            foreground=_LIGHT.get(r["level"], _LIGHT["green"]))

    def _update_run_button(self):
        if not self.sel:
            return
        mine = self.data_source.get() == "mine"
        if mine and not self.user_file:
            self.btn_run.config(text=I18N.t("pick_first"), state="disabled")
        else:
            self.btn_run.config(text=I18N.t("run_mine") if mine else I18N.t("run_example"), state="normal")

    # ---------- 运行 ----------
    def _run(self):
        if not self.sel:
            return
        if not find_rscript():
            self._locate_r()
            return
        params = self.form.values() if self.form else {}
        input_path = self.user_file if self.data_source.get() == "mine" else None
        self.run = engine.Run(self.sel, input_path=input_path, params=params)
        self._set_log("")
        self.results.clear()
        self.nb.select(0)
        self.btn_run.config(state="disabled")
        self.btn_cancel.pack(side="left", padx=8)
        self.run.start()
        self.root.after(120, self._poll)

    def _poll(self):
        if not self.run:
            return
        for kind, payload in self.run.poll():
            if kind == "log":
                self._append_log(payload)
            elif kind == "error":
                self._append_log("✗ " + str(payload))
            elif kind == "done":
                self._on_done(payload)
                return
        self.root.after(120, self._poll)

    def _on_done(self, rc):
        r = self.run
        self.btn_cancel.pack_forget()
        self.btn_open.pack(side="left", padx=8)
        self._update_run_button()
        imgs = [o for o in r.outputs if o.lower().endswith(".png")]
        tbls = [o for o in r.outputs if o.lower().endswith(".csv")]
        if rc == 0:
            self.results.show(r.outputs)
            self.nb.select(1)
            self._append_log("\n" + I18N.t("done_ok", rc=rc, nimg=len(imgs), ntbl=len(tbls)))
        else:
            self._append_log("\n" + I18N.t("done_fail", rc=rc))

    def _cancel(self):
        if self.run:
            self.run.cancel()

    def _open_folder(self):
        if self.run and self.run.outdir.exists():
            try:
                os.startfile(str(self.run.outdir))
            except Exception:
                pass

    # ---------- R 定位 ----------
    def _locate_r(self):
        if messagebox.askokcancel(I18N.t("no_r_title"), I18N.t("no_r_body")):
            path = filedialog.askopenfilename(title="Rscript.exe", filetypes=[("Rscript", "Rscript.exe"), ("All", "*.*")])
            if path:
                set_rscript(os.path.normpath(path))
                self._apply_r_status()

    # ---------- 工具 ----------
    def _show_detail(self, show):
        # 未选方法时也展示占位;这里仅控制运行按钮/结果区在有方法时可用
        if not show:
            self.lbl_method.config(text="🪽 Meta Wingman")
            self.lbl_desc.config(text=I18N.t("select_method"))

    def _set_log(self, text):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", text)
        self.log.config(state="disabled")

    def _append_log(self, line):
        self.log.config(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.config(state="disabled")
