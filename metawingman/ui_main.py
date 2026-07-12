# -*- coding: utf-8 -*-
"""主窗口:左=分组方法树,右=方法详情。RevMan 式紧凑、克制,无营销文案。
性能:红绿灯去主线程(缓存+防抖+后台线程);参数表单按方法缓存不重建。"""
from __future__ import annotations
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog

from . import engine
from . import theme
from .i18n import I18N
from .form import ParamForm
from .results import ResultsView
from .redlight import estimate as mem_estimate
from .rlocate import find_rscript, set_rscript


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.sel = None
        self.data_source = tk.StringVar(value="example")
        self.user_file = None
        self.run = None
        self._forms = {}          # method_id -> ParamForm(缓存,避免重建)
        self._rl_job = None
        self._rl_tok = 0
        self._rl_q = queue.Queue()

        root.geometry("1120x720")
        root.minsize(900, 600)
        self._build_top()
        self._build_body()
        I18N.bind(self._on_lang)
        self._select_first()

    def _init_sash(self):
        try:
            self._vpane.sashpos(0, 372)   # 固定分隔:控件区在上、结果区在下
        except Exception:
            pass

    def _select_first(self):
        n2m = getattr(self, "_node_to_mid", {})
        target = "meta_pairwise" if "meta_pairwise" in n2m.values() else None
        for node, mid in n2m.items():
            if target is None or mid == target:
                self.tree.selection_set(node)
                self.tree.see(node)
                self.pick(mid)
                return

    # ---------- 顶栏(极简) ----------
    def _build_top(self):
        top = ttk.Frame(self.root, padding=(12, 6))
        top.pack(side="top", fill="x")
        self.lbl_rstat = ttk.Label(top, style="Muted.TLabel")
        self.lbl_rstat.pack(side="left")
        self.btn_lang = ttk.Button(top, width=6, style="Toolbutton", command=I18N.toggle)
        self.btn_lang.pack(side="right")
        ttk.Separator(self.root, orient="horizontal").pack(side="top", fill="x")

    # ---------- 主体 ----------
    def _build_body(self):
        body = ttk.Frame(self.root)
        body.pack(side="top", fill="both", expand=True)

        left = ttk.Frame(body, padding=(6, 6))
        left.pack(side="left", fill="y")
        self.tree = ttk.Treeview(left, show="tree", selectmode="browse")
        self.tree.column("#0", width=230, minwidth=190)
        self.tree.tag_configure("group", font=(theme.FONT, 9, "bold"))
        self.tree.pack(side="left", fill="y", expand=True)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        ttk.Separator(body, orient="vertical").pack(side="left", fill="y")

        right = ttk.Frame(body, padding=(14, 10))
        right.pack(side="left", fill="both", expand=True)
        # ★垂直 PanedWindow:控件区(top)与结果区(bottom)用固定 sash 隔开,
        #   改方法标题/参数不再牵动下方 Notebook 重排(实测省掉每次 ~60ms 卡顿)。
        vpane = ttk.PanedWindow(right, orient="vertical")
        vpane.pack(fill="both", expand=True)
        self._vpane = vpane
        top = ttk.Frame(vpane)
        bottom = ttk.Frame(vpane)

        # 方法标题 + 次级(另一语言)
        self.lbl_method = ttk.Label(top, style="Method.TLabel", wraplength=720)
        self.lbl_method.pack(anchor="w")
        self.lbl_sub = ttk.Label(top, style="Muted.TLabel", wraplength=720)
        self.lbl_sub.pack(anchor="w", pady=(1, 8))

        # 数据段
        self.hdr_data = ttk.Label(top, style="Section.TLabel")
        self.hdr_data.pack(anchor="w", pady=(4, 2))
        ttk.Separator(top, orient="horizontal").pack(fill="x", pady=(0, 6))
        ds = ttk.Frame(top)
        ds.pack(fill="x")
        self.rb_ex = ttk.Radiobutton(ds, variable=self.data_source, value="example", command=self._on_source)
        self.rb_ex.grid(row=0, column=0, sticky="w", padx=(0, 16))
        self.rb_mine = ttk.Radiobutton(ds, variable=self.data_source, value="mine", command=self._on_source)
        self.rb_mine.grid(row=0, column=1, sticky="w")
        self.btn_file = ttk.Button(ds, style="Toolbutton", command=self._choose_file)
        self.btn_file.grid(row=0, column=2, sticky="w", padx=16)
        self.lbl_file = ttk.Label(ds, style="Muted.TLabel")
        self.lbl_file.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))
        self.lbl_cols = ttk.Label(ds, style="Muted.TLabel", wraplength=680, justify="left")
        self.lbl_cols.grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))
        self.lbl_mem = ttk.Label(ds, style="Muted.TLabel")
        self.lbl_mem.grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 0))

        # 参数段
        self.hdr_params = ttk.Label(top, style="Section.TLabel")
        self.hdr_params.pack(anchor="w", pady=(12, 2))
        ttk.Separator(top, orient="horizontal").pack(fill="x", pady=(0, 6))
        self.params_host = ttk.Frame(top)   # 缓存的表单挂这里
        self.params_host.pack(fill="x")

        # 运行行
        rowb = ttk.Frame(top)
        rowb.pack(fill="x", pady=(10, 4))
        self.btn_run = ttk.Button(rowb, style="Accent.TButton", command=self._run)
        self.btn_run.pack(side="left")
        self.btn_cancel = ttk.Button(rowb, style="Toolbutton", command=self._cancel)

        # 日志 / 结果
        self.nb = ttk.Notebook(bottom)
        self.nb.pack(fill="both", expand=True)
        vpane.add(top, weight=0)
        vpane.add(bottom, weight=1)
        self.root.after(80, lambda: self._init_sash())
        logf = ttk.Frame(self.nb)
        self.log = tk.Text(logf, height=7, wrap="word", font=(theme.MONO, 9),
                           background=theme.CANVAS, foreground=theme.TEXT,
                           relief="flat", borderwidth=0)
        lsb = ttk.Scrollbar(logf, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set, state="disabled")
        self.log.pack(side="left", fill="both", expand=True)
        lsb.pack(side="right", fill="y")
        self.results = ResultsView(self.nb, on_open_folder=self._open_folder)
        self.nb.add(logf, text="Log")
        self.nb.add(self.results, text="Results")

    # ---------- 语言刷新 ----------
    def _on_lang(self):
        self.btn_lang.config(text=I18N.t("lang_button"))
        self.rb_ex.config(text=I18N.both("use_example"))
        self.rb_mine.config(text=I18N.both("use_mine"))
        self.btn_file.config(text=I18N.t("choose_file"))
        self.btn_cancel.config(text=I18N.t("cancel"))
        self.hdr_data.config(text=I18N.t("data"))
        self.hdr_params.config(text=I18N.t("parameters"))
        self.nb.tab(0, text=I18N.t("log"))
        self.nb.tab(1, text=I18N.t("results"))
        self.results.retitle()
        self._apply_r_status()
        self._rebuild_tree()
        if self.sel:
            self._render_header()
        else:
            self.lbl_method.config(text="Meta Wingman")
            self.lbl_sub.config(text=I18N.t("select_method"))
        self._update_run_button()

    def _apply_r_status(self):
        ok = bool(find_rscript())
        self.lbl_rstat.config(text=(I18N.t("r_ok") if ok else I18N.t("r_missing")),
                              foreground=theme.OK if ok else theme.SIG)

    # ---------- 方法树 ----------
    def _rebuild_tree(self):
        self.tree.delete(*self.tree.get_children())
        self._node_to_mid = {}
        lang = I18N.lang
        for key, zh, en, items in engine.grouped_methods():
            parent = self.tree.insert("", "end", text=(zh if lang == "zh" else en), open=True, tags=("group",))
            for m in items:
                node = self.tree.insert(parent, "end", text=I18N.title_of(m))
                self._node_to_mid[node] = m["id"]
        if self.sel:
            for node, mid in self._node_to_mid.items():
                if mid == self.sel["id"]:
                    self.tree.selection_set(node)
                    break

    def _on_select(self, _evt):
        node = (self.tree.selection() or [None])[0]
        mid = getattr(self, "_node_to_mid", {}).get(node)
        if mid and (not self.sel or mid != self.sel["id"]):
            self.pick(mid)

    # ---------- 选方法 ----------
    def pick(self, mid):
        self.sel = engine.load_manifest(mid)
        self.data_source.set("example")
        self.user_file = None
        self._render_header()
        self._swap_form(mid)
        self._set_log("")
        self.results.clear()
        self._refresh_file_label()
        self._schedule_redlight()
        self._update_run_button()

    def _render_header(self):
        m = self.sel
        self.lbl_method.config(text=I18N.title_of(m))
        other = m.get("title") if I18N.lang == "en" else m.get("title_en")
        self.lbl_sub.config(text=other or "")
        pin = engine.primary_input(m)
        spec = (pin or {}).get("spec", "")
        self.lbl_cols.config(text=(I18N.t("columns_needed") + ": " + spec) if spec else "")

    def _swap_form(self, mid):
        for f in self._forms.values():
            f.pack_forget()
        if mid not in self._forms:
            self._forms[mid] = ParamForm(self.params_host, self.sel.get("params_schema"))
        self._forms[mid].pack(fill="x")

    @property
    def form(self):
        return self._forms.get(self.sel["id"]) if self.sel else None

    def _on_source(self):
        if self.data_source.get() == "mine" and not self.user_file:
            self._choose_file()
            return
        self._refresh_file_label()
        self._schedule_redlight()
        self._update_run_button()

    def _choose_file(self):
        path = filedialog.askopenfilename(
            title="CSV", filetypes=[("CSV", "*.csv"), ("Text", "*.txt *.tsv"), ("All", "*.*")])
        if path:
            self.user_file = os.path.normpath(path)
            self.data_source.set("mine")
        else:
            if not self.user_file:
                self.data_source.set("example")
        self._refresh_file_label()
        self._schedule_redlight()
        self._update_run_button()

    def _refresh_file_label(self):
        if self.data_source.get() == "mine" and self.user_file:
            self.lbl_file.config(text=I18N.t("loaded") + ": " + os.path.basename(self.user_file))
        else:
            self.lbl_file.config(text="")

    def _cur_data_path(self):
        if self.data_source.get() == "mine":
            return self.user_file
        return engine.example_path(self.sel) if self.sel else None

    # ---------- 红绿灯(防抖 + 后台线程) ----------
    def _schedule_redlight(self):
        if self._rl_job:
            self.root.after_cancel(self._rl_job)
        self.lbl_mem.config(text="")
        self._rl_job = self.root.after(150, self._run_redlight)

    def _run_redlight(self):
        self._rl_job = None
        m, path = self.sel, self._cur_data_path()
        if not m:
            return
        tok = self._rl_tok = self._rl_tok + 1
        # worker 只塞队列(Tkinter 非线程安全,worker 不碰 Tk);主线程 after 轮询回填
        threading.Thread(target=lambda: self._rl_q.put((tok, mem_estimate(m, path))), daemon=True).start()
        self.root.after(50, lambda: self._poll_redlight(tok))

    def _poll_redlight(self, tok):
        if tok != self._rl_tok:
            return                       # 已有更新请求,弃本轮
        latest = None
        try:
            while True:
                latest = self._rl_q.get_nowait()
        except queue.Empty:
            pass
        if latest and latest[0] == self._rl_tok:
            self._apply_redlight(latest[1])
        else:
            self.root.after(50, lambda: self._poll_redlight(tok))

    def _apply_redlight(self, r):
        if not r:
            self.lbl_mem.config(text="")
            return
        dims = f'{r.get("n_rows", "?")}×{r.get("n_cols", "?")}'
        self.lbl_mem.config(
            text=f'{I18N.t("memory")}: {dims} · ' + I18N.t("peak_mem", gb=r["peak_gb"], avail=r["avail_gb"]),
            foreground=theme.LIGHT.get(r["level"], theme.OK))

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
                self._append_log("! " + str(payload))
            elif kind == "done":
                self._on_done(payload)
                return
        self.root.after(120, self._poll)

    def _on_done(self, rc):
        r = self.run
        self.btn_cancel.pack_forget()
        self._update_run_button()
        imgs = [o for o in r.outputs if o.lower().endswith(".png")]
        tbls = [o for o in r.outputs if o.lower().endswith(".csv")]
        if rc == 0:
            self.results.show(r.outputs, r.outdir)
            self.nb.select(1)
            self._append_log("\n" + I18N.t("done_ok", rc=rc, nimg=len(imgs), ntbl=len(tbls)))
        else:
            self._append_log("\n" + I18N.t("done_fail", rc=rc))

    def _cancel(self):
        if self.run:
            self.run.cancel()

    def _open_folder(self):
        d = self.run.outdir if self.run else None
        if d and d.exists():
            try:
                os.startfile(str(d))
            except Exception:
                pass

    # ---------- R 定位 ----------
    def _locate_r(self):
        from tkinter import messagebox
        if messagebox.askokcancel(I18N.t("no_r_title"), I18N.t("no_r_body")):
            path = filedialog.askopenfilename(title="Rscript.exe", filetypes=[("Rscript", "Rscript.exe"), ("All", "*.*")])
            if path:
                set_rscript(os.path.normpath(path))
                self._apply_r_status()

    # ---------- 工具 ----------
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
