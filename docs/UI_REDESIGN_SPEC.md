========== layout_target ==========
见上

========== quick_wins ==========
按"改一处、两 App 同惠、当天见效"排序的 P0 清单:
1) theme.py:apply() 一次改齐(见 C1):加 Body 中间字阶、启用 SURFACE 做分区带/状态栏/树分组行、配 Treeview.Heading 浅灰底、TNotebook.Tab 活动页加粗、TSeparator 用 BORDER。纯 Style,零布局风险,theme.py 与 form.py 两 App 字节相同→自动双惠。这一条就把"满屏纯白 9pt 灰字"的单调感去掉大半。
2) 删 _run() 里的 self.nb.select(0)(ui_main.py:714)与 _on_done 的 self.nb.select(1)(763):即便暂不做抽屉,先让 Results 常驻可见、日志不再抢屏——最小改动直击【日志占比】。
3) 接线已就绪却零引用的 download_template(i18n.py:56/122):在数据段加一个"下载示例作模板"Toolbutton,复制 engine.example_path(self.sel)。三行代码补上【输入引导】最缺的"示例在哪"。
4) results.py:_table_tab 结果表加隔行底纹 tree.tag_configure("odd", background=theme.SURFACE) 并按奇偶打 tag(第 270 行插行处):专业感白送。
5) _init_sash(ui_main.py:167-170):把固定 sashpos(0,372) 改成按高度百分比(见 C2 代码),结果区立即变主。
先做 1+2+5(结构与观感),再补 3+4(引导与细节),半天内三诉求都能看到肉眼改善。

========== principles ==========
见上

========== input_guidance_design ==========
目标:把引导从"上传后才在映射下拉里露出列信息 + 一行 spec 文字"前移成"选方法瞬间就把'要什么数据、列长什么样、示例在哪、上传后对不对'讲清楚",全程用已有的 manifest/shape 数据驱动,不需新造后端。

数据源(全部现成,零后端改动):
- 一行格式串:engine.primary_input(m)["spec"](现仅喂 lbl_cols,ui_main.py:426-428)
- 结构化列规格:engine.shape_of(m).columns → 每列 {role, zh, en, type, required, aliases}(config/column_shapes.json,现仅在 _rebuild_map 610-620 上传后露出)
- 真实示例文件:engine.example_path(m)(engine.py:66-70,现只用于运行,从未展示)
- 已备好却零引用的文案:download_template(i18n.py:56/122)

引导五步(选方法 → 运行前):

第 1 步「选方法即出'输入格式卡'」——在数据段(hdr_data 下、数据源单选之后、map_frame 之前)常驻一个 ttk.Labelframe(Card 样式,标题"输入格式 / Input format",默认展开,example 与 mine 两种模式都可见,补上当前默认 example 无引导的空档)。pick() 里调 _refresh_input_card() 刷新。纯参数无形状的方法(shape 为空且无 example)则 pack_forget 优雅隐藏。

第 2 步「列规格表(该方法要哪些列)」——卡内一个只读 ttk.Treeview(show=headings,height≈4,columns=列名/含义/类型/必填),逐行读 shape.columns:列名=role、含义=zh·en、类型=type、必填=required?"必填":"选填"。必填行用 tag 前景 TEXT、选填行 MUTED 区分轻重。这把"需要哪几列、每列含义、哪些必填"从上传后前移到选完方法即见。

第 3 步「示例前三行(你的文件应长这样)」——卡内第二个只读 Treeview,表头=真实示例 CSV 的列名、数据=example_path 的前 3 行(新增 _read_rows(path,n),沿用 _read_headers 的 utf-8-sig/gb18030/latin-1 多编码兜底)。用"活样板"替代抽象规格,直接回答"列长什么样"。行数限 3,避免喧宾夺主。

第 4 步「一键取数(示例在哪 + 怎么开始)」——卡内按钮行两颗 Toolbutton:①"下载示例作模板"(接线 download_template):filedialog.asksaveasfilename 后 shutil.copyfile(example_path, dst),给出可照填的真实模板;②"用示例填录入表格"(仅 tksheet 可用时):把示例前几行灌进 grid_frame 的 sheet,用户直接改成自己的数据免列映射。两颗都指向"先跑通一次看正确长相"。

第 5 步「上传后的校验反馈」——增强 _rebuild_map(600-620):(a)每个必填角色若 _guess 猜空(值为"(无)"),其 label 前景染 theme.SIG 并加"*";(b)map_frame 顶部加一行汇总 Label,绑定各 Combobox 的 <<ComboboxSelected>> 实时刷新:全部必填已对应→"✓ 必填列已齐(绿 OK)",否则→"! 还差 N 列:研究标签、效应量…"(红 SIG)。把现在"运行时才在日志里报 map_missing"(704)的滞后校验,变成映射当场的即时反馈。同时数据载入后 lbl_mem 的 n_rows×n_cols 红绿灯(674-677)已是"活"的维度回执,保留即可。

文案:input_format / hdr_column / hdr_meaning / hdr_type / hdr_required / required / fill_example / map_ok / map_missing_n 全部按 i18n.py 双语补齐(download_template 已就绪);Meta 与 Bio 两份 STRINGS 同步。整套只加"读现成 manifest/shape/example 渲染"的 UI 代码,不改后端、不碰性能敏感的切换路径(卡的刷新只在 pick 时发生,不进 76ms 热路)。

========== risks ==========
1) 结构改造(C2)动了 self.nb 的全部引用(创建 323-324、add 344-345、tab 重命名 364-365、select 705/714/739/763),漏改一处会 AttributeError——必须一次性梳理干净,建议先全局搜 self.nb 列清单再改。2) pack 顺序陷阱:日志抽屉 side=bottom 必须在 vpane.pack(expand=True) 之前注册,否则 expand 控件先吃满 cavity、抽屉分到 0 高;状态栏 side=bottom 也必须早于 body 的 pack。3) sashpos 必须在控件 realize 后设(after + winfo_height 判 >50 再设),过早调用被忽略;折叠/展开要记住上次高度避免跳。4) vista 自绘控件红线:别给 ttk.Button/Entry/Combobox/Labelframe 上背景色,分区带一律用 tk.Frame+tk.Label;Treeview 行 tag background 在部分 vista 版本支持有限,分组行浅灰若不生效退回 bold-only。5) 输入卡/搜索/校验的内容质量依赖 manifest 补 group/help 字段与真实示例文件——是内容工作不是 UI 风险,但占位空壳会砸引导招牌,示例必须真能跑通产图。6) 两 App 同步:ui_main.py 除品牌串外字节相同,改动需镜像到 bio-wingman(仅 26 处品牌差异);theme.py/form.py 相同自动双惠;i18n.py/results.py 结构并行,新键/隔行底纹两边都要加。7) 报错可发现性是硬底线:去掉"运行即跳日志"后,必须保留 rc≠0 自动展开抽屉+状态点 SIG,否则用户看不到失败原因。

========== CHANGES (8) ==========
[P0] C1 — theme.py 视觉地基:四级字阶 + 启用 SURFACE 分区带 + 配 Heading/Tab/Separator  (effort=小)
  解决: 单调,总体专业感
  文件: theme.py:apply
  现状: theme.py:25-38 apply() 只配 3 档字阶(Method12/Section9bold/Muted9),SURFACE #F5F6F7 与 BORDER #DADDE1 已定义(theme.py:11-12)却从未使用;Notebook.Tab/Treeview.Heading/TSeparator 全走 vista 原生未配;全界面纯白 CANVAS 无分区。
  改法: 一次性在 apply() 内:①新增 Body.TLabel(9/TEXT)补中间层级、Method 提到 13;②用 SURFACE 定义 Zone/Status 的 tk 用底色常量与 ZoneTitle 文字样式;③Treeview.Heading 配 SURFACE 底、TNotebook.Tab 活动页加粗、TSeparator 用 BORDER;④Treeview rowheight 22→24 让树呼吸。纯 Style,不动布局,theme.py 两 App 字节相同→自动双惠。
  代码骨架:
def apply(style):
    style.configure("Treeview", font=(FONT,9), rowheight=24, indent=14,
                    borderwidth=0, background=CANVAS, fieldbackground=CANVAS)
    style.map("Treeview", background=[("selected", ACCENT_SOFT)], foreground=[("selected", TEXT)])
    # 四级字阶(新增 Body 中间层级)
    style.configure("Method.TLabel",  font=(FONT,13,"bold"), foreground=TEXT)
    style.configure("Section.TLabel", font=(FONT,9,"bold"), foreground=MUTED)
    style.configure("Body.TLabel",    font=(FONT,9),        foreground=TEXT)
    style.configure("Muted.TLabel",   font=(FONT,9),        foreground=MUTED)
    style.configure("Mono.TLabel",    font=(MONO,9),        foreground=TEXT)
    # 结果表/schema 卡表头:浅灰底拉层次(vista 可控)
    style.configure("Treeview.Heading", font=(FONT,9,"bold"), foreground=TEXT,
                    background=SURFACE, relief="flat")
    style.map("Treeview.Heading", background=[("active", ACCENT_SOFT)])
    # Notebook 活动页加粗(results.py 内部 Notebook 同惠)
    style.configure("TNotebook", background=CANVAS, borderwidth=0)
    style.configure("TNotebook.Tab", font=(FONT,9), padding=(10,4))
    style.map("TNotebook.Tab", font=[("selected",(FONT,9,"bold"))])
    style.configure("TSeparator", background=BORDER)
    style.configure("TButton", font=(FONT,10), padding=(12,4))
    style.configure("Accent.TButton", font=(FONT,10,"bold"), padding=(14,5))
    style.configure("Toolbutton", font=(FONT,9), padding=(8,3))
    # 分区带/状态栏用经典 tk 上色,常量在此暴露给 ui_main:
    #   band = tk.Frame(parent, bg=theme.SURFACE); tk.Label(band, bg=theme.SURFACE, ...)
  风险: vista 可能忽略部分 map(如 Tab 的 selected font 在个别版本);Heading/Separator/rowheight 可靠。纯样式、可回退,风险低。

[P0] C2 — 拆掉 Log/Results 平权 Notebook:结果直升主 pane,日志降为可折叠抽屉  (effort=中)
  解决: 日志占比,单调,总体专业感
  文件: ui_main.py:_build_body / _run / _on_done / _on_lang / _data_ok / _append_log
  现状: ui_main.py:322-345 下 pane 是 Notebook{Log=tab0 默认选中, Results=tab1},各占满整块 bottom;_run 每次 self.nb.select(0) 跳日志(714),仅 _on_done 成功 select(1)(763);_data_ok 失败也 select(0)(739);_on_lang 用 self.nb.tab(0/1) 重命名(364-365)。启动到运行中主视区一直是空白日志。
  改法: ①ResultsView 直接挂到 bottom pane(去掉中间 Notebook),常驻可见;②tk.Text 日志移进 right 底部的'抽屉':26px SURFACE 标题带(状态点+▸折叠钮+最新一行摘要)+ 默认 pack_forget 的抽屉体;③_run 删 select(0),改为写状态点+状态栏;④_on_done rc==0 走 results.show(已有)、状态点 OK 绿、不强开日志;rc≠0 自动展开抽屉+状态点 SIG 红;⑤清理所有 self.nb 引用(364-365 改 results.retitle()+日志钮重贴;739 改 _open_log())。★pack 顺序:抽屉 side=bottom 必须在 vpane.pack(expand) 之前。
  代码骨架:
# --- bottom pane = 结果本体 ---
self.results = ResultsView(bottom, on_open_folder=self._open_folder)
self.results.pack(fill="both", expand=True)
# --- 日志抽屉:先建先 pack(side=bottom),再 pack vpane ---
self._log_open = False
drawer = ttk.Frame(right)
hdr = tk.Frame(drawer, bg=theme.SURFACE); hdr.pack(side="top", fill="x")
ttk.Separator(hdr, orient="horizontal").pack(side="top", fill="x")
self._dot = tk.Canvas(hdr, width=10, height=10, highlightthickness=0, bg=theme.SURFACE)
self._dot.pack(side="left", padx=(8,6), pady=4)
self._dot_id = self._dot.create_oval(2,2,8,8, fill=theme.MUTED, outline="")
self.btn_log = ttk.Button(hdr, style="Toolbutton", command=self._toggle_log); self.btn_log.pack(side="left")
self.lbl_logtail = tk.Label(hdr, bg=theme.SURFACE, fg=theme.MUTED, font=(theme.FONT,9))
self.lbl_logtail.pack(side="left", padx=8)
self._log_body = ttk.Frame(drawer)
self.log = tk.Text(self._log_body, height=7, wrap="word", font=(theme.MONO,9),
                   background=theme.CANVAS, foreground=theme.TEXT, relief="flat", borderwidth=0)
lsb = ttk.Scrollbar(self._log_body, orient="vertical", command=self.log.yview)
self.log.configure(yscrollcommand=lsb.set, state="disabled")
self.log.pack(side="left", fill="both", expand=True); lsb.pack(side="right", fill="y")
drawer.pack(side="bottom", fill="x")      # ★在 vpane.pack 之前
vpane.pack(side="top", fill="both", expand=True)
vpane.add(top_outer, weight=0); vpane.add(bottom, weight=1)

def _toggle_log(self, force=None):
    self._log_open = (not self._log_open) if force is None else force
    (self._log_body.pack(side="top", fill="x") if self._log_open else self._log_body.pack_forget())
    self.btn_log.config(text=("▾ " if self._log_open else "▸ ") + I18N.t("log"))

def _set_dot(self, color):
    self._dot.itemconfig(self._dot_id, fill=color)
# _append_log 末尾追加: self.lbl_logtail.config(text=line[:80])
# _run: 去掉 self.nb.select(0); self._set_dot(theme.WARN); self._set_status(I18N.t('running'))
# _on_done: rc==0 -> self._set_dot(theme.OK); self._set_status(I18N.t('r_ok'))
#           rc!=0 -> self._toggle_log(True); self._set_dot(theme.SIG)
  风险: self.nb 引用遗漏会 AttributeError(先全局搜清单);pack side=bottom 顺序错会让抽屉高 0;报错可发现性硬底线=rc≠0 必自动展开+红点。ResultsView 内部自有 Notebook 不受影响,只换父容器。

[P0] C3 — 底部状态栏 + sash 改百分比:接管实时反馈,让结果成主区  (effort=小)
  解决: 日志占比,总体专业感,单调
  文件: ui_main.py:__init__ / _build_status(新) / _init_sash / _apply_redlight / _apply_r_status
  现状: ui_main.py 无底部状态栏;运行反馈只靠切日志 tab。_init_sash(167-170)固定 sashpos(0,372) 令控件区(372)反比结果区(293)大。红绿灯维度在 _apply_redlight(670-677)已算好但只喂 lbl_mem。
  改法: ①root 最底 pack 一条 24px 状态栏(tk.Frame bg=SURFACE):左状态文字、中 indeterminate Progressbar(仅运行时 pack+start)、右上下文(维度+R 版本)、Sizegrip;状态栏 side=bottom 必须早于 body。②_apply_redlight 末尾把维度写进右侧 lbl_ctx。③_init_sash 改按 pane 高度 44%,realize 后再设。日志得以安心收起。
  代码骨架:
def _build_status(self):
    bar = tk.Frame(self.root, bg=theme.SURFACE)
    bar.pack(side="bottom", fill="x")           # ★早于 body.pack
    ttk.Separator(bar, orient="horizontal").pack(side="top", fill="x")
    inner = tk.Frame(bar, bg=theme.SURFACE); inner.pack(fill="x", padx=8, pady=2)
    self.lbl_status = tk.Label(inner, bg=theme.SURFACE, fg=theme.MUTED, font=(theme.FONT,9))
    self.lbl_status.pack(side="left")
    ttk.Sizegrip(inner).pack(side="right")
    self.lbl_ctx = tk.Label(inner, bg=theme.SURFACE, fg=theme.MUTED, font=(theme.FONT,9))
    self.lbl_ctx.pack(side="right", padx=8)
    self.pbar = ttk.Progressbar(inner, mode="indeterminate", length=120)  # 仅运行时 pack

def _set_status(self, text):
    self.lbl_status.config(text=text)

def _init_sash(self):
    try:
        self._vpane.update_idletasks()
        h = self._vpane.winfo_height()
        if h < 50:
            self.root.after(60, self._init_sash); return
        self._vpane.sashpos(0, int(h*0.44))
    except Exception: pass
# _apply_redlight 末尾: self.lbl_ctx.config(text=f'{dims} · R')
# _run: self.pbar.pack(side="left", padx=8); self.pbar.start(12)
# _on_done: self.pbar.stop(); self.pbar.pack_forget()
  风险: Progressbar indeterminate 用 after 轮询驱动、勿阻塞主线程(现 _poll 已 after 120ms,天然安全)。tk.Label 上色可靠;状态栏与日志抽屉标题带别叠成两条平行栏(抽屉在 right 内、状态栏跨全窗,层级不冲突)。

[P0] C4 — 选方法即出'输入格式卡':列规格表 + 示例前三行 + 下载模板/填示例  (effort=中)
  解决: 输入引导,单调,总体专业感
  文件: ui_main.py:_build_input_card(新) / _refresh_input_card(新) / _read_rows(新) / _download_template(新) / pick / _on_lang
  现状: ui_main.py:_render_header(421-428)只把 spec 拼成 lbl_cols 一行灰字;列结构(shape.columns 的 zh/en/type/required)只有上传后在 _rebuild_map(610-620)露出;example_path(engine.py:66-70)从不展示;download_template(i18n.py:56/122)零引用。默认 example 与常用 mine 都无同级格式提示。
  改法: 数据段内(lbl_mem 之后、paste/grid/map 之前)常驻一个 Card 样式 Labelframe(标题'输入格式'),pick() 调 _refresh_input_card():①只读 Treeview 列出 shape.columns(列名/含义/类型/必填);②只读 Treeview 展示 example 前 3 行真实数据(新增 _read_rows 复用多编码兜底);③按钮'下载示例作模板'(接线 download_template,copyfile example_path)+'用示例填录入表格'(灌进 tksheet)。纯参数无形状方法 pack_forget 隐藏。
  代码骨架:
def _build_input_card(self, parent):
    self.card = ttk.Labelframe(parent)
    btns = ttk.Frame(self.card); btns.pack(fill="x", padx=8, pady=(6,2))
    self.btn_tmpl = ttk.Button(btns, style="Toolbutton", command=self._download_template); self.btn_tmpl.pack(side="left")
    self.btn_fill = ttk.Button(btns, style="Toolbutton", command=self._fill_example_grid); self.btn_fill.pack(side="left", padx=(6,0))
    self.tv_schema = ttk.Treeview(self.card, show="headings", height=4, columns=("c","d","t","r"))
    for c,w in (("c",130),("d",230),("t",70),("r",64)):
        self.tv_schema.column(c, width=w, stretch=False, anchor="w")
    self.tv_schema.pack(fill="x", padx=8, pady=(2,4))
    self.tv_prev = ttk.Treeview(self.card, show="headings", height=3)
    self.tv_prev.pack(fill="x", padx=8, pady=(0,8))

def _read_rows(self, path, n):
    if not path or not os.path.exists(path): return [], []
    for enc in ("utf-8-sig","gb18030","latin-1"):
        try:
            with open(path, encoding=enc, newline="") as f:
                rows=[[c.strip() for c in r] for i,r in enumerate(csv.reader(f)) if i<=n]
            return (rows[0] if rows else []), rows[1:n+1]
        except UnicodeDecodeError: continue
        except Exception: return [], []
    return [], []

def _refresh_input_card(self):
    shape = engine.shape_of(self.sel); ex = engine.example_path(self.sel)
    self.tv_schema.heading("c", text=I18N.both("hdr_column")); self.tv_schema.heading("d", text=I18N.both("hdr_meaning"))
    self.tv_schema.heading("t", text=I18N.both("hdr_type"));   self.tv_schema.heading("r", text=I18N.both("hdr_required"))
    self.tv_schema.delete(*self.tv_schema.get_children())
    if shape:
        for c in shape["columns"]:
            self.tv_schema.insert("", "end", values=(c["role"], f'{c.get("zh")} · {c.get("en")}',
                c.get("type","-"), I18N.t("required") if c.get("required") else I18N.t("optional")))
    hdr, rows = self._read_rows(ex, 3)
    self.tv_prev["columns"] = list(range(len(hdr)))
    self.tv_prev.delete(*self.tv_prev.get_children())
    for i,h in enumerate(hdr):
        self.tv_prev.heading(i, text=h); self.tv_prev.column(i, width=90, stretch=False, anchor="w")
    for r in rows: self.tv_prev.insert("", "end", values=r)
    (self.card.pack(fill="x", pady=(6,2)) if (shape or hdr) else self.card.pack_forget())

def _download_template(self):
    ex = engine.example_path(self.sel)
    if not ex or not os.path.exists(ex): return
    dst = filedialog.asksaveasfilename(defaultextension=".csv",
        initialfile=self.sel["id"]+"_template.csv", filetypes=[("CSV","*.csv")])
    if dst: shutil.copyfile(ex, dst)
  风险: 示例表限 3 行防喧宾夺主;读示例沿用多编码兜底;新键 hdr_column/hdr_meaning/hdr_type/hdr_required/required/fill_example 两 App i18n 双语补齐(download_template 已就绪)。刷新只在 pick 时发生,不进 76ms 切换热路。

[P1] C5 — 上传后即时校验反馈:必填未映射标红 + 汇总行  (effort=小)
  解决: 输入引导,总体专业感
  文件: ui_main.py:_rebuild_map / _map_feedback(新)
  现状: ui_main.py:_rebuild_map(600-620)每角色一个 Combobox,label 一律 Muted 灰;必填缺失只在运行时 _run(704)写日志 map_missing、并 nb.select(0),校验滞后且不显眼。
  改法: ①_rebuild_map 里:必填角色若 _guess 猜空,label 前景染 theme.SIG 并加'*';②map_frame 底部加一行汇总 tk.Label,绑定各 Combobox 的 <<ComboboxSelected>> 调 _map_feedback():全部必填已对应→OK 绿'✓ 必填列已齐',否则→SIG 红'! 还差 N 列: …'。把滞后校验变即时反馈。复用现有 _missing_required(630-635)。
  代码骨架:
# _rebuild_map 内,建完所有 Combobox 后:
self.lbl_mapfb = tk.Label(self.map_frame, font=(theme.FONT,9), anchor="w")
self.lbl_mapfb.grid(row=len(shape["columns"])+1, column=0, columnspan=2, sticky="w", pady=(4,0))
for role,(var,col) in self._map_vars.items():
    # 找到该行 label 引用,必填猜空则:lbl.config(foreground=theme.SIG, text=... + " *")
    pass
# 每个 Combobox: cb.bind("<<ComboboxSelected>>", lambda e: self._map_feedback())
self._map_feedback()

def _map_feedback(self):
    miss = self._missing_required()
    if miss:
        self.lbl_mapfb.config(fg=theme.SIG,
            text="! " + I18N.t("map_missing_n", n=len(miss)) + ": " + "、".join(miss))
    else:
        self.lbl_mapfb.config(fg=theme.OK, text="✓ " + I18N.t("map_ok"))
  风险: 必填红边只用语义 SIG、不做动画;需在 _rebuild_map 建 label 时留引用以便染色(现是匿名 ttk.Label,改成先存再 grid)。新键 map_ok/map_missing_n 双语补齐。

[P1] C6 — 参数表单分层:Body 字阶 label + 右对齐 + 可选分组/说明  (effort=小)
  解决: 单调,总体专业感,输入引导
  文件: form.py:ParamForm.__init__
  现状: form.py:8-33 ParamForm 每行 ttk.Label(默认字体,无 style)+ 控件,两列 grid 扁平无分组、无说明;label 列不定宽。form.py 两 App 字节相同。
  改法: ①label 套 Body.TLabel、label 列固定宽右对齐得规整感;②读可选 spec['group'] → 用 ttk.Labelframe 分组(常用在上、'高级'收一组);③读可选 spec['help'] → 控件下方 Muted 小字说明。全部对 schema 缺字段向后兼容(无 group/help 时行为不变)。manifest 加 group/help 是内容工作,先上样式即见效。
  代码骨架:
for key, spec in props.items():
    title = spec.get("title", key)
    lbl = ttk.Label(self, text=title, style="Body.TLabel")
    lbl.grid(row=row, column=0, sticky="e", padx=(0,12), pady=5)   # 右对齐规整
    # ... 原 enum/boolean/entry 控件不变 ...
    w.grid(row=row, column=1, sticky="w", pady=5)
    help = spec.get("help")
    if help:
        ttk.Label(self, text=help, style="Muted.TLabel").grid(
            row=row+1, column=1, sticky="w", pady=(0,4)); row += 1
    self.vars[key] = (var, typ); row += 1
self.columnconfigure(0, minsize=110)
self.columnconfigure(1, weight=1)
  风险: 低,纯样式+可选字段;分组要 manifest 配 group 才生效,否则退回单容器。label 右对齐在个别超长中文标题下需 wraplength 兜底。

[P1] C7 — 方法树即时搜索 + 分组行浅灰带  (effort=小)
  解决: 单调,导航
  文件: ui_main.py:_build_body(left) / _rebuild_tree
  现状: ui_main.py:217-226 树无搜索;_rebuild_tree(382-395)分组仅 tag 'group' 9pt 加粗,背景与叶子同 CANVAS,层级浅;61 叶平铺难定位。
  改法: ①left 树上方 pack 一个 ttk.Entry(占位'搜索方法/Filter'),<KeyRelease> 触发带 query 的 _rebuild_tree,对中英双标题不分大小写子串匹配,命中则插入并展开父组、空组不插、清空复原、按 self.sel 复选;②tree.tag_configure('group', background=theme.SURFACE) 让分组成浅灰带。选中态维持单一 ACCENT_SOFT。
  代码骨架:
# left 内,树之前:
self.q_var = tk.StringVar()
ent = ttk.Entry(left, textvariable=self.q_var)
ent.pack(side="top", fill="x", pady=(0,4))
ent.bind("<KeyRelease>", lambda e: self._rebuild_tree(self.q_var.get().strip()))
# 树:
self.tree.tag_configure("group", background=theme.SURFACE, font=(theme.FONT,9,"bold"))

def _rebuild_tree(self, query=""):
    q = query.lower()
    self.tree.delete(*self.tree.get_children()); self._node_to_mid = {}
    for key, zh, en, items in engine.grouped_methods():
        hits = [m for m in items if (not q)
                or q in I18N.title_of(m).lower()
                or q in (str(m.get("title",""))+str(m.get("title_en",""))).lower()]
        if not hits: continue
        parent = self.tree.insert("", "end", text=(zh if I18N.lang=="zh" else en), open=True, tags=("group",))
        for m in hits:
            node = self.tree.insert(parent, "end", text=I18N.title_of(m))
            self._node_to_mid[node] = m["id"]
    if self.sel:
        for node, mid in self._node_to_mid.items():
            if mid == self.sel["id"]: self.tree.selection_set(node); break
  风险: Treeview 行 tag background 在部分 vista 版本支持有限→不生效则退回 bold-only;过滤保持 _node_to_mid 与选中态一致;中英双标题都要能被搜到。全量重建树 61 叶实测无卡顿(不触右侧重排)。

[P2] C8 — 顶栏升级品牌带 + 控件区/结果区各戴分区标题带  (effort=小)
  解决: 单调,总体专业感
  文件: ui_main.py:_build_top / _zone_header(新) / _build_body
  现状: ui_main.py:203-210 顶栏 ttk.Frame padding(12,6) 仅 R 状态+语言键,视觉重量为零;控件区(top,244-)与结果区无区头,是一条扁平堆叠。
  改法: ①顶栏改 tk.Frame(bg=SURFACE)+底部 Separator,左加产品名 tk.Label(YaHei 11)+R 状态点,右语言键——给顶部重量,不加营销;②做可复用 _zone_header(parent, title) = tk.Frame(bg=SURFACE)+Section 文字+底 1px Separator,给控件区顶('方法/Method')与结果区顶('结果/Results')各戴一顶,和日志抽屉标题带统一节奏。纯 tk 上色可靠。
  代码骨架:
def _zone_header(self, parent, title):
    band = tk.Frame(parent, bg=theme.SURFACE)
    tk.Label(band, text=title, bg=theme.SURFACE, fg=theme.TEXT,
             font=(theme.FONT,9,"bold")).pack(side="left", padx=8, pady=3)
    ttk.Separator(band, orient="horizontal")  # 由调用方 pack 在 band 下
    return band

def _build_top(self):
    top = tk.Frame(self.root, bg=theme.SURFACE); top.pack(side="top", fill="x")
    inner = tk.Frame(top, bg=theme.SURFACE); inner.pack(fill="x", padx=12, pady=6)
    tk.Label(inner, text=I18N.t("app_title"), bg=theme.SURFACE, fg=theme.TEXT,
             font=(theme.FONT,11,"bold")).pack(side="left")
    self.lbl_rstat = tk.Label(inner, bg=theme.SURFACE, font=(theme.FONT,9))
    self.lbl_rstat.pack(side="left", padx=12)
    self.btn_lang = ttk.Button(inner, width=6, style="Toolbutton", command=I18N.toggle)
    self.btn_lang.pack(side="right")
    ttk.Separator(self.root, orient="horizontal").pack(side="top", fill="x")
# 注:_apply_r_status 改为 self.lbl_rstat.config(fg=...) (tk.Label 用 fg 非 foreground 亦可)
  风险: lbl_rstat 由 ttk.Label 改 tk.Label,_apply_r_status 的 foreground= 需保持可用(tk.Label 接受 fg/foreground 均可);app_title 已在 i18n。分区带只用 SURFACE 一档灰,别滑向卡片观感。
