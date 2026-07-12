I have full ground truth on the repo: the 11 current manifests, the adapter→`_common.R`→toolkit source chain, the manifest JSON schema, the toolkit module numbering, and confirmation that `00_device.R` + `00a_theme_nature.R` are already vendored into `meta-wingman/toolkit/R/` (so `_common.R` auto-loads them for every adapter). Here is the consolidated build spec.

---

# Meta Wingman — Build Spec (single source of truth)

Reconciles the platform-union inventory, the 58-leaf list, and the already-vendored Nature theme into one implementation-ready plan. Canonical leaf IDs (`#1…#58`) are stable across all five sections. Reusable R lives in **`meta-analysis-toolkit`** (`github.com/fsy2004/meta-analysis-toolkit`), vendored into `meta-wingman/toolkit/`; the launcher only adds thin `run_*.R` adapters + `manifests/*.json`.

Repo facts this spec is built on:
- Current adapters (11): `run_pairwise · run_proportion · run_heterogeneity · run_influence · run_network · run_diagnostic · run_bayesian · run_grade · run_prisma · run_rob · run_dataprep_msd`.
- Each `run_*.R` does `source(_common.R)`; `_common.R` sources **every** file in `toolkit/R/` in sorted order → the Nature theme (`00a_theme_nature.R`) is already in scope for all adapters.
- One manifest = one left-tree menu item. Params are CLI flags (`param_flags` maps schema→flag).

---

## 1. FINAL fine-grained left-tree (target)

Legend: `[X]` = currently an output bundled inside existing adapter *X* (to be surfaced as its own leaf); **`[NEW]`** = method not yet in the product. Leaf `#` = canonical ID (matches §2). Every FIGURE leaf renders through the shared Nature theme (§3).

```
META WINGMAN  元分析僚机
│
├─ 1  核心合并 Core Synthesis
│   ├─ 1.1 成对 Pairwise
│   │    ├─ #1  Pairwise forest (binary/continuous) 成对森林图 ............ [pairwise]
│   │    ├─ #2  Generic inverse-variance forest 通用倒方差森林 ............ [pairwise]
│   │    ├─ #3  Pooled effect summary (FE+RE, Q/I²/τ²/H²) 合并汇总表 ...... [pairwise]
│   │    └─ #4  Correlation meta-analysis (Fisher z) 相关系数合并 ......... [NEW]
│   ├─ 1.2 稀有/零事件 Rare & zero-event
│   │    ├─ #5  Mantel–Haenszel OR 稀有事件MH ........................... [NEW]
│   │    ├─ #6  Peto OR Peto法 ......................................... [NEW]
│   │    └─ #7  Binomial-normal GLMM 二项-正态GLMM ..................... [NEW]
│   ├─ 1.3 生存 Time-to-event
│   │    └─ #8  Hazard-ratio meta-analysis 生存HR合并 .................. [NEW]
│   ├─ 1.4 单臂比例 Proportion
│   │    ├─ #9  Proportion — logit 单臂比例(logit) ..................... [proportion]
│   │    ├─ #10 Proportion — random-intercept GLMM 比例GLMM ........... [proportion/NEW]
│   │    └─ #11 Proportion — Freeman–Tukey 双反正弦 ................... [NEW]
│   └─ 1.5 单臂均值/率 Single-arm mean/rate
│        └─ #12 Single-arm mean · incidence rate 单臂均值·发生率 ....... [NEW]
│
├─ 2  异质性与调节 Heterogeneity & Moderators
│   ├─ #13 Heterogeneity statistics panel 异质性统计量 ................ [heterogeneity]
│   ├─ #14 Subgroup analysis + forest 亚组分析 ....................... [heterogeneity]
│   ├─ #15 Meta-regression + bubble plot 元回归气泡图 ................. [heterogeneity]
│   ├─ #16 Prediction-interval forest 预测区间森林 ................... [NEW]
│   └─ #17 Permutation test for meta-reg 置换检验元回归 .............. [NEW]
│
├─ 3  小研究效应与发表偏倚 Small-study & Publication Bias
│   ├─ 3.1 漏斗 Funnel
│   │    └─ #18 Contour-enhanced funnel 等高线漏斗图 ................. [pairwise]
│   ├─ 3.2 回归检验 Regression tests
│   │    ├─ #19 Egger regression test Egger回归 ..................... [pairwise]
│   │    └─ #20 Begg rank test Begg秩相关 ........................... [pairwise]
│   ├─ 3.3 校正 Adjustment
│   │    ├─ #21 Trim-and-fill 剪补法 ................................ [pairwise]
│   │    ├─ #22 PET-PEESE ........................................... [pairwise]
│   │    ├─ #23 Limit meta-analysis (Rücker) 极限元分析 ............. [NEW]
│   │    └─ #24 Copas selection model Copas选择模型 ................ [NEW]
│   └─ 3.4 诊断散点 Diagnostic scatter
│        ├─ #25 L'Abbé plot L'Abbé图 ............................... [NEW]
│        └─ #26 Radial (Galbraith) plot 放射图 ..................... [NEW]
│
├─ 4  稳健性与影响 Robustness & Influence
│   ├─ #27 Leave-one-out forest 逐一剔除 ............................ [influence]
│   ├─ #28 Baujat plot Baujat图 ..................................... [influence]
│   ├─ #29 Cumulative meta-analysis 累积元分析 ...................... [influence]
│   ├─ #30 GOSH plot GOSH图 ......................................... [influence]
│   └─ #31 Influence diagnostics (Cook/hat/DFBETAS) 影响诊断 ........ [NEW]
│
├─ 5  复杂数据结构 Complex Data Structures
│   ├─ #32 Three-level meta-analysis 三层元分析 ..................... [NEW]
│   ├─ #33 Robust variance estimation (RVE) 稳健方差估计 ............ [NEW]
│   ├─ #34 Dose-response — linear 剂量反应线性 ...................... [NEW]
│   └─ #35 Dose-response — cubic spline 剂量反应样条 ................ [NEW]
│
├─ 6  网络meta NMA
│   ├─ #36 Network graph 网络几何图 ................................. [network]
│   ├─ #37 NMA forest vs reference 网络森林图 ....................... [network]
│   ├─ #38 League table 联赛表 ...................................... [network]
│   ├─ #39 SUCRA / P-score ranking 排序概率 ........................ [network]
│   ├─ #40 Rankogram 秩图 ........................................... [network]
│   ├─ #41 Node-splitting (SIDE) 节点分割 .......................... [network]
│   ├─ #42 Design-by-treatment / net heat 设计交互·热图 ............ [NEW]
│   ├─ #43 Comparison-adjusted funnel 比较校正漏斗图 ............... [NEW]
│   ├─ #44 Component NMA (additive) 成分网络meta ................... [NEW]
│   └─ #45 CINeMA confidence 证据确信度 ............................ [NEW]
│
├─ 7  诊断准确性 Diagnostic Test Accuracy
│   ├─ #46 Bivariate SROC (Reitsma) 双变量SROC ..................... [diagnostic]
│   ├─ #47 Paired sens/spec forest 敏感度特异度森林 ................ [diagnostic]
│   ├─ #48 LR / DOR summary 似然比·诊断OR ......................... [NEW]
│   └─ #49 HSROC model HSROC模型 ................................... [NEW]
│
├─ 8  贝叶斯 Bayesian
│   ├─ #50 Bayesian RE forest 贝叶斯随机效应森林 ................... [bayesian]
│   └─ #51 Posterior density (μ, τ) 后验密度 ...................... [bayesian]
│
├─ 9  序贯与效能 Sequential & Power
│   ├─ #52 Trial Sequential Analysis (TSA) 试验序贯分析 ............ [NEW]
│   └─ #53 Required information size / OIS 所需信息量 .............. [NEW]
│
├─ 10 证据确信度与偏倚敏感 Certainty & Bias Sensitivity
│   ├─ #54 E-value (point+CI) E值敏感性 ............................ [NEW]
│   ├─ #55 GRADE Summary-of-Findings GRADE证据总表 ................. [grade]
│   └─ #56 RoB2 traffic-light + summary 偏倚风险图 ................. [rob]
│
├─ 11 报告 Reporting
│   └─ #57 PRISMA 2020 flow PRISMA流程图 ........................... [prisma]
│
└─ 12 数据准备 Data Preparation
     └─ #58 Median/IQR→mean±SD + effect-size converters 数据换算 ... [dataprep_msd]
```

Coverage check — every current-11 output lands on a leaf: pairwise→#1/#2/#3/#18/#19/#20/#21/#22; proportion→#9/#10; heterogeneity→#13/#14/#15; influence→#27/#28/#29/#30; network→#36–#41; diagnostic→#46/#47; bayesian→#50/#51; grade→#55; rob→#56; prisma→#57; dataprep_msd→#58. **11 coarse adapters → 58 leaves; 27 surfaced from existing outputs, 31 NEW.**

---

## 2. Build table (58 leaves)

Split = SPLIT (surface an output already produced by adapter *X*) / NEW (new method). Batch: **A** = zero new R install · **B** = needs a new CRAN pkg · **C** = advanced/external. Prio: P1 first release · P2 second · P3 advanced.

| # | Leaf (EN / 中文) | Category | R pkg::fn | Split / New | Batch | Prio |
|---|---|---|---|---|---|---|
| 1 | Pairwise forest / 成对森林 | 1.1 Pairwise | `meta::metabin`,`metacont`,`forest` | SPLIT(pairwise) | A | P1 |
| 2 | Generic IV forest / 通用倒方差 | 1.1 | `meta::metagen`,`forest` | SPLIT(pairwise) | A | P1 |
| 3 | Pooled summary table / 汇总表 | 1.1 | `ma_summary_row`,`meta::summary` | SPLIT(pairwise) | A | P1 |
| 4 | Correlation MA / 相关合并 | 1.1 | `meta::metacor` | NEW | A | P2 |
| 5 | Mantel–Haenszel OR / MH | 1.2 Rare | `metafor::rma.mh` | NEW | A | P2 |
| 6 | Peto OR / Peto | 1.2 | `metafor::rma.peto` | NEW | A | P2 |
| 7 | GLMM (zero-event) / 二项GLMM | 1.2 | `metafor::rma.glmm` | NEW | A | P2 |
| 8 | HR meta-analysis / 生存HR | 1.3 | `meta::metagen`(logHR,se) | NEW | A | P2 |
| 9 | Proportion logit / 比例logit | 1.4 | `meta::metaprop(sm="PLOGIT")` | SPLIT(proportion) | A | P1 |
| 10 | Proportion GLMM / 比例GLMM | 1.4 | `meta::metaprop(method="GLMM")` | SPLIT/NEW | A | P2 |
| 11 | Freeman–Tukey / 双反正弦 | 1.4 | `meta::metaprop(sm="PFT")` | NEW | A | P3 |
| 12 | Single-arm mean/rate / 均值·率 | 1.5 | `meta::metamean`,`metarate` | NEW | A | P3 |
| 13 | Heterogeneity panel / 异质性 | 2 | `meta::summary`,`metafor::confint` | SPLIT(heterogeneity) | A | P1 |
| 14 | Subgroup + forest / 亚组 | 2 | `meta::update(subgroup=)` | SPLIT(heterogeneity) | A | P1 |
| 15 | Meta-reg + bubble / 元回归 | 2 | `metafor::rma`,`regplot` | SPLIT(heterogeneity) | A | P1 |
| 16 | Prediction-interval forest / 预测区间 | 2 | `meta::forest(prediction=TRUE)` | NEW | A | P1 |
| 17 | Permutation test / 置换检验 | 2 | `metafor::permutest` | NEW | A | P3 |
| 18 | Contour funnel / 等高线漏斗 | 3.1 | `meta::funnel(contour=)` | SPLIT(pairwise) | A | P1 |
| 19 | Egger test / Egger | 3.2 | `metafor::regtest` | SPLIT(pairwise) | A | P1 |
| 20 | Begg test / Begg | 3.2 | `metafor::ranktest` | SPLIT(pairwise) | A | P2 |
| 21 | Trim-and-fill / 剪补 | 3.3 | `metafor::trimfill` | SPLIT(pairwise) | A | P1 |
| 22 | PET-PEESE | 3.3 | `metafor::escalc`+`lm` | SPLIT(pairwise) | A | P2 |
| 23 | Limit meta-analysis / 极限 | 3.3 | `metasens::limitmeta` | NEW | A | P3 |
| 24 | Copas model / Copas | 3.3 | `metasens::copas` | NEW | A | P3 |
| 25 | L'Abbé plot / L'Abbé | 3.4 | `meta::labbe` | NEW | A | P2 |
| 26 | Radial plot / 放射图 | 3.4 | `metafor::radial` | NEW | A | P2 |
| 27 | Leave-one-out / 逐一剔除 | 4 | `metafor::leave1out` | SPLIT(influence) | A | P1 |
| 28 | Baujat / Baujat | 4 | `metafor::baujat` | SPLIT(influence) | A | P2 |
| 29 | Cumulative / 累积 | 4 | `metafor::cumul` | SPLIT(influence) | A | P2 |
| 30 | GOSH / GOSH | 4 | `metafor::gosh` | SPLIT(influence) | A | P3 |
| 31 | Influence diagnostics / 影响诊断 | 4 | `metafor::influence` | NEW | A | P2 |
| 32 | Three-level MA / 三层 | 5 | `metafor::rma.mv` | NEW | A | P2 |
| 33 | RVE / 稳健方差 | 5 | `robumeta::robu`,`clubSandwich` | NEW | **B** | P2 |
| 34 | Dose-response linear / 剂量线性 | 5 | `dosresmeta::dosresmeta` | NEW | **B** | P2 |
| 35 | Dose-response spline / 剂量样条 | 5 | `dosresmeta`+`rms::rcs` | NEW | **B** | P3 |
| 36 | Network graph / 网络图 | 6 | `netmeta::netgraph` | SPLIT(network) | A | P1 |
| 37 | NMA forest / 网络森林 | 6 | `netmeta::forest.netmeta` | SPLIT(network) | A | P1 |
| 38 | League table / 联赛表 | 6 | `netmeta::netleague` | SPLIT(network) | A | P1 |
| 39 | SUCRA/P-score / 排序 | 6 | `netmeta::netrank` | SPLIT(network) | A | P1 |
| 40 | Rankogram / 秩图 | 6 | `netmeta::rankogram` | SPLIT(network) | A | P2 |
| 41 | Node-splitting / 节点分割 | 6 | `netmeta::netsplit` | SPLIT(network) | A | P1 |
| 42 | Net heat / 设计交互热图 | 6 | `netmeta::decomp.design`,`netheat` | NEW | A | P2 |
| 43 | Comparison-adjusted funnel / 比较校正漏斗 | 6 | `netmeta::funnel.netmeta` | NEW | A | P2 |
| 44 | Component NMA / 成分NMA | 6 | `netmeta::netcomb`,`discomb` | NEW | A | P3 |
| 45 | CINeMA / 确信度 | 6 | `netmeta` contrib + CINeMA | NEW | **C** | P3 |
| 46 | Bivariate SROC / 双变量SROC | 7 | `mada::reitsma` | SPLIT(diagnostic) | A | P1 |
| 47 | Paired sens/spec forest / 配对森林 | 7 | `mada::forest`,`madad` | SPLIT(diagnostic) | A | P1 |
| 48 | LR/DOR summary / 似然比 | 7 | `mada::madad`,`SummaryPts` | NEW | A | P2 |
| 49 | HSROC / HSROC | 7 | `CopulaDTA`/adv. | NEW | **C** | P3 |
| 50 | Bayesian RE forest / 贝叶斯森林 | 8 | `bayesmeta::bayesmeta` | SPLIT(bayesian) | A | P2 |
| 51 | Posterior density / 后验 | 8 | `bayesmeta::plot` | SPLIT(bayesian) | A | P2 |
| 52 | TSA / 试验序贯 | 9 | `RTSA::RTSA` | NEW | **B** | P2 |
| 53 | Required info size / 信息量 | 9 | `RTSA`(design) | NEW | **B** | P3 |
| 54 | E-value / E值 | 10 | `EValue::evalue` | NEW | **B** | P2 |
| 55 | GRADE SoF / 证据总表 | 10 | toolkit `ma_grade`+`gridExtra` | SPLIT(grade) | A | P1 |
| 56 | RoB2 traffic-light / 偏倚风险 | 10 | `robvis::rob_traffic_light` | SPLIT(rob) | A | P1 |
| 57 | PRISMA 2020 / 流程图 | 11 | `PRISMA2020` or `DiagrammeR` | SPLIT(prisma) | A/B | P1 |
| 58 | Median/IQR→mean±SD + converters / 数据换算 | 12 | `estmeansd`,`metafor::escalc` | SPLIT(dataprep) | A | P1 |

**Batch totals: A = 50 · B = 6 (`#33,#34,#35,#52,#53,#54`) · C = 2 (`#45,#49`).** New CRAN packages required by Batch B: `robumeta`, `clubSandwich`, `dosresmeta`, `rms`, `RTSA`, `EValue` (all CRAN, Tsinghua mirror). `PRISMA2020` is optional for #57 (else `DiagrammeR`, Batch A).

---

## 3. Nature figure theme — one theme, every adapter (already vendored)

**Status: built and vendored.** `00a_theme_nature.R` exists in both `meta-analysis-toolkit/R/` (canonical) and `meta-wingman/toolkit/R/` (runtime). Because `_common.R` sources every `toolkit/R/*.R` in sorted order, the theme functions are already in scope for **all 11 current + all future adapters** — no per-adapter import needed. `00_device.R` provides `mw_pdf` (cairo, embeds Arial); `00a_` sorts right after it so the app's real device wins and the theme only adds functions.

### 3a. The spec (sourced from Nature's Guide to Preparing Final Artwork + research-figure-guide)

| Property | Nature rule | Encoded as |
|---|---|---|
| Font | Helvetica/**Arial**, one family throughout | `NATURE_SPEC$font`; `mw_pdf(family=)` |
| Text size | **7 pt max, 5 pt min** at print size | `theme_nature(base_size=7)`; device `pointsize=7` |
| Tick labels | 5–7 pt (use ~6) | `axis.text = base_size−1` |
| Panel labels a,b,c | **8 pt bold lowercase** | `plot.tag`; `plot_annotation(tag_levels="a")` |
| Line weight | **0.25–1 pt** (hairline 0.25, data/axis 0.5) | `line_hair_pt`,`line_data_pt` |
| Ticks | short outward, real marks | ggplot `axis.ticks.length=2pt`; base `tcl=-0.30` |
| Chart-junk | no bold titles, no gridlines, no 3-D/shadows | blank grid/bg/legend rect; plain title |
| Colour | colour-blind safe | Okabe–Ito `nature_pal()` |
| Width | 1-col **88 mm**, 2-col **180 mm** | `nature_width_in("single"/"double")` |
| Export | vector PDF; ≥300 dpi bitmap | `nature_pdf()` / `nature_png(dpi=300)` |

Sources: [Nature final-artwork PDF](https://www.nature.com/documents/nature-final-artwork.pdf) · [research-figure-guide specifications](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/) · [Okabe–Ito palette](https://jfly.uni-koeln.de/color/).

### 3b. The reusable R (all in `00a_theme_nature.R`; abridged to the load-bearing exports)

```r
NATURE_SPEC <- list(font="Arial", font_max_pt=7, font_min_pt=5, panel_tag_pt=8,
  line_data_pt=0.5, line_hair_pt=0.25, width_single_mm=88, width_double_mm=180,
  dpi_bitmap=300,
  palette=c("#000000","#E69F00","#56B4E9","#009E73","#F0E442","#0072B2","#D55E00","#CC79AC"))

## ggplot: theme_nature(base_size=7, border=FALSE, grid="none") + scale_*_nature()
##   text size is literal pt; lines converted pt->mm via ggplot2::.pt so 0.25/0.5pt land exactly.
## base graphics: nature_base()  -> sets par(family, cex.axis=6/7, lwd=0.5pt->lwd, tcl=-0.30, mgp, mar)
##   returns list(cex, cex.axis, lwd, lwd.hair, tcl, font, pal) to hand into forest()/funnel()/netgraph().
## devices (both embed Arial via cairo, open at pointsize=7 so cex 1 == 7pt):
##   nature_pdf(out, size="single"|"double"|<mm>, height_mm=, pointsize=7)  # calls nature_base()
##   nature_png(out, ..., dpi=300)      # ragg fallback grDevices::png(type="cairo")
##   nature_ggsave(out, plot, size=, height_mm=)  # ggsave(device=mw_pdf)
```

### 3c. Wiring — how ALL adapters share it (via the toolkit)

The theme is loaded automatically. What remains is **applying it at each figure call site inside the toolkit modules** (`06_forest.R`, `04_publication_bias.R`, `05_influence.R`, `20_network_meta.R`, `21_diagnostic_meta.R`, …), so every leaf inherits it without adapter-level work:

- **Base-graphics figures** (`metafor::forest/funnel/radial/baujat`, `meta::labbe/drapery`, `netmeta::netgraph/netheat`, `mada` SROC, `bayesmeta`): replace `grDevices::pdf(out,w,h)` with `nature_pdf(out, size="double", height_mm=H)`, then `cx <- nature_base()` and pass `cex=cx$cex`, `lwd=cx$lwd` into the plot call.
- **ggplot figures** (bubble, rankogram-as-ggplot, robvis, GRADE table): append `+ theme_nature()` (+ `scale_colour_nature()`), save via `nature_ggsave()`.
- **`to_png()`** in `_common.R` already rasterizes the PDF for the UI — unchanged.

Migration is one line per figure function (~14 toolkit modules). New leaves must open with `nature_pdf()`/`theme_nature()` per `CONVENTIONS.md §0` ("no plain bar charts"; forest/funnel/lollipop/SROC/rankogram/violin only). **All new reusable figure/stat code goes into `meta-analysis-toolkit/R/`, then vendor-syncs to `meta-wingman/toolkit/R/`** — adapters stay thin.

---

## 4. Build order (fastest → slowest)

**Wave 1 — Batch A, SPLIT of existing, P1 (~18 leaves, days).** Pure surfacing: the toolkit functions already run and already emit these figures inside the 11 adapters. Work = split each bundled output into its own manifest + add an `--analysis` selector (see §5). Leaves: `#1 #2 #3 #9 #13 #14 #15 #18 #19 #21 #27 #36 #37 #38 #39 #41 #46 #47 #55 #56 #57 #58`. Also do the §3c theme wiring here (touches the same modules). Ships a complete, submission-grade menu with zero installs.

**Wave 2 — Batch A, NEW, zero-install, P2 then P3 (~30 leaves).** New toolkit functions over already-installed packages (`metafor`/`meta`/`netmeta`/`mada`/`bayesmeta`/`metasens`). P2 first: `#4 #5 #6 #7 #8 #10 #16 #20 #22 #25 #26 #28 #29 #31 #32 #40 #42 #43 #48 #50 #51`. Then P3: `#11 #12 #17 #23 #24 #30 #44`. netmeta covers all NMA leaves (`#40 #42 #43 #44`) with no install; metasens covers `#23 #24`.

**Wave 3 — Batch B, add packages then implement (6 leaves).** Add `robumeta clubSandwich dosresmeta rms RTSA EValue` (and optionally `PRISMA2020`) to `requirements`/`install.bat`, verify on Tsinghua+Gitee mirror, then build `#33 #34 #35 #52 #53 #54`. New input shapes `[dose]`, `[+clst]`.

**Wave 4 — Batch C, advanced/external (2 leaves).** `#45 CINeMA` (approximate locally via `netmeta::netcontrib` first; full CINeMA behind Docker/web later) and `#49 HSROC` (`CopulaDTA`/Bayesian). Optional; not blocking.

Per-batch count: **A = 50 (Wave 1 ≈ 20 + Wave 2 ≈ 30) · B = 6 · C = 2 = 58.**

---

## 5. Execution model — recommendation

**Recommended: one manifest per leaf (58 menu items) served by ~12 shared "family" adapters selected with a `--analysis` flag.** Not 58 R files, not 58 outputs-per-adapter. This keeps the plugin contract intact (the left tree is 1:1 with manifests) while collapsing R code to roughly the current file count.

Why this and not the two extremes:
- *One adapter+manifest per leaf (58 `run_*.R`)* — cleanest conceptually but 58 near-duplicate scripts, 58× the boilerplate, and re-fits the same `ma_fit` object many times when a user clicks forest then funnel.
- *Few adapters, each emitting many figures (today's model)* — few files but the menu can't expose leaves individually; violates the fine left-tree the whole spec is built for.

The family-adapter middle path exploits the existing pattern: `run_pairwise.R` already builds one `ma_fit` and derives forest/funnel/bias from it. Add `--analysis <leaf>` so each manifest calls the same adapter but selects one output.

**Family → leaves map (12 adapters, 58 manifests):**

| Adapter (input shape) | Leaves | `--analysis` values |
|---|---|---|
| `run_pairwise.R` `[2x2]/[cont]/[gen]` | 1,2,3,4,5,6,7,8,18,19,20,21,22,25,26 | forest / gen_forest / summary / corr / mh / peto / glmm / hr / funnel / egger / begg / trimfill / petpeese / labbe / radial |
| `run_proportion.R` `[prop]` | 9,10,11,12 | logit / glmm / ft / mean_rate |
| `run_heterogeneity.R` `[+cov]` | 13,14,15,16,17 | stats / subgroup / metareg / pred_forest / permute |
| `run_influence.R` (pooled) | 27,28,29,30,31 | loo / baujat / cumulative / gosh / diagnostics |
| `run_complex.R` (NEW) `[+clst]/[dose]` | 32,33,34,35 | ml3 / rve / dose_linear / dose_spline |
| `run_network.R` `[net]` | 36–45 | graph / forest / league / rank / rankogram / nodesplit / netheat / cadj_funnel / component / cinema |
| `run_diagnostic.R` `[dta]` | 46,47,48,49 | sroc / paired_forest / lr_dor / hsroc |
| `run_bayesian.R` `[gen]` | 50,51 | forest / posterior |
| `run_sequential.R` (NEW) | 52,53 | tsa / ris |
| `run_evalue.R` (NEW) | 54 | evalue |
| `run_grade.R` / `run_rob.R` / `run_prisma.R` / `run_dataprep.R` | 55 / 56 / 57 / 58 | (single output each) |

Net: **~12 adapter files, 58 manifests, 58 menu leaves.** Rules to keep it clean:
1. Each manifest hard-codes its leaf via `param_flags` (e.g. `"analysis": "--analysis"` with a fixed default), so the UI shows a single-purpose card; the `--analysis` param is not user-editable (omit from `params_schema`, set in a fixed `args` field or default).
2. Manifests in a family **share the same input shape + example CSV**, so users upload once and can run any sibling analysis on the same data.
3. Adapters build the heavy object once (`ma_pairwise` / `netmeta` / `reitsma`) then `switch(analysis, …)` to the requested figure — no redundant refits, and shared bias/heterogeneity stats come free.
4. Manifest `group` + `item_order` reproduce the §1 tree ordering in the left panel; `family` = the §1 category label (EN+中文).

This preserves "one manifest per leaf" (the plugin promise) and the fine-grained tree, while keeping the R surface at ~12 maintainable files that reuse the already-tested toolkit — consistent with the vendored-toolkit + manifest-driven architecture and the "reuse real tool code, no fabricated APIs" rule.

---

Files inspected (all absolute): `C:\Users\fsy\Desktop\meta-wingman\config.json`, `...\manifests\meta_pairwise.json`, `...\manifests\meta_network.json`, `...\adapters\meta\_common.R`, `...\adapters\meta\run_pairwise.R`; `C:\Users\fsy\Desktop\meta-analysis-toolkit\docs\CONVENTIONS.md`; toolkit `R\` (16 modules incl. `00_device.R`, `00a_theme_nature.R`, both already vendored to `meta-wingman\toolkit\R\`).