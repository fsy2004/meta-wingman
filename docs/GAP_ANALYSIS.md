# Meta Wingman vs RevMan/CMA — Prioritized Gap Analysis & Roadmap

Synthesis of four studies (RevMan/CMA inventory · MetaInsight code · JASP/jamovi code · core R ecosystem). Meta Wingman is already **statistically broader** than either competitor; every genuine gap is in the **review-authoring / structured-workflow / reproducibility / trust** layer, plus a short list of high-value R functions not yet wrapped.

---

## 1. Executive gap summary — the 5 biggest things to beat RevMan/CMA

1. **No saveable project file** — every analysis is a throwaway; nothing to reopen, revise, or hang a review on. This blocks everything else. (Both competitors have it; you have none.)
2. **No structured review tree** (comparison → outcome → subgroup) — the conceptual heart of RevMan that turns a pile of analyses into *a review*.
3. **No RoB-judgement or GRADE/SoF workflow** — you only *render* robvis/SoF if handed a table; the mandatory 90% (structured judgement capture, GRADE certainty logic) is missing. This is Cochrane table-stakes neither CMA has.
4. **No auto-written Methods/Results text + Word/reproducible-R-script + citations export** — the reporting layer. Largely free for you because your manifest+adapter already *is* the exact R call; `metafor::reporter()` does most of it in one function.
5. **No in-app data-entry grid with typed validation** — the daily interaction mode of both competitors, and a first line of defense for result credibility (events ≤ total, SD > 0).

---

## 2. Gaps by theme

Effort is rated for your **Tkinter + R-adapter + JSON-manifest** architecture and installed toolchain (Pandoc 3.9, LibreOffice, python-docx-capable Python, R 4.4.3). S = days, M = 1–2 weeks, L = multi-week / architectural.

### (a) Review/project model & data management

| Gap | What / why | Best-in-class + file to learn from | Effort |
|---|---|---|---|
| **Saveable project file** | One `.mwproj` bundle (JSON or SQLite) = `{app, version, data, column_mapping, per-analysis params, cached results}`. Without it nothing is iterable. | **MetaInsight** `inst/shiny/modules/core_save.R` + `setup_reload.R`: every module returns a `list(save=…, load=…)` closure pair; bundle stamps `app`/`version` and **gates on the stamp** on reload ("not a valid save file" / version-mismatch warning). CMA `.cma` proves users expect it. | **S** |
| **Structured review tree** (comparison→outcome→subgroup) | A `ttk.Treeview` navigator; each leaf binds to one of your 61 analyses over a shared study set; drives SoF + results text. The thing that makes it *a review*, not a calculator. | RevMan data model (Handbook 4.8). `meta::metabind()` is the R-side template for binding subgroup/outcome/sensitivity models into one grouped-row forest. Depends on the project file. | **L** |
| **Global "excluded studies" set** | One app-wide exclusion selection drives a *second* copy of every analysis so each result shows **primary vs. sensitivity side-by-side**; for pairwise MA this *is* leave-one-out. | **MetaInsight** `setup_exclude.R`: `common$excluded_studies` → `common$subsetted_data`; every module renders `plot_all` beside `plot_sub`; debounced cancellable recompute; click-to-toggle. | **M** |

### (b) Data entry & effect-size input

| Gap | What / why | Best-in-class + file | Effort |
|---|---|---|---|
| **In-app data-entry grid** | Type/edit/correct data in place with per-outcome-type column templates + inline validation. Competitors' core interaction; cuts entry error. | CMA spreadsheet + RevMan typed tables. Use `tksheet` (or editable `ttk.Treeview`). Validation pattern from **MetaInsight** `R/setup_load_f.R` → `ValidateUploadedData()`: an **ordered validator chain** returning `{valid, message}` with study-named messages ("Some studies have R > N: Smith2019"). | **M** |
| **Effect-size computation wizard** | Guided **Design → Measurement → Measure** cascade (each dropdown filters the next) that emits computed `yi/vi` *and* the `escalc()` code. | **JASP** `inst/qml/EffectSizeComputation.qml` + `R/effectsizecomputation.R` (maps triple → `escalc(measure=…)`, prints the call). MAJOR's alternative = separate analyses per input shape. | **M** |
| **Summary-stat reconstruction converters** | `metafor::conv.fivenum()` (median/IQR/range → mean/SD; Wan/Luo/Shi, built-in skewness check), `conv.2x2()`, `conv.wald()` (CI/p → SE), `conv.delta()`. The most-requested extraction helpers in modern reviews. | **metafor** — thin adapters over existing functions. | **S–M** |
| **Full `escalc` measure catalog** | Expose ~100 measures reviewers now ask for: `VR`/`CVR` (variability), `ROM`, pre-post `SMCC/SMCR/SMCRH`, `D2ORL/D2ORN` (SMD↔logOR). | **metafor** `escalc()`. | **S** (per measure) |
| **Wide↔long auto-detect + case-insensitive headers** | Detect shape, match headers loosely, live guidance panel per format/outcome toggle. | **MetaInsight** `FindDataShape()`/`WideToLong()`/`.FixColumnNameCases()`; `setup_load.R` JS-toggled guidance. | **S** |

### (c) Risk-of-Bias & GRADE workflows

| Gap | What / why | Best-in-class + source | Effort |
|---|---|---|---|
| **RoB judgement entry UI** | Domain forms for **RoB 2 / ROBINS-I / QUADAS-2** with published **signalling-question algorithms** that *propose* a domain judgement the user confirms/overrides + "support for judgement" free-text; then pass straight into the robvis rendering you already have. Mandatory in Cochrane/PRISMA; neither CMA nor JASP/jamovi has it — a real differentiator. | RoB 2 starter pack / Excel tool algorithms (freely specified). robvis templates (ROB2/ROBINS-I/QUADAS-2/ROB1). Forms are plain Tkinter; value = the domain templates. | **M** |
| **GRADE / SoF workflow** | Encode the 5 downgrade + 3 upgrade domains → certainty per outcome; SoF table computes absolute effects from pooled relative effect + assumed baseline risk (easy R). Expected in guideline-grade reviews; RevMan needs external GRADEpro — doing it *in-app* beats them. | RevMan↔GRADEpro spec. Best built **after** the review tree (C1) so outcomes exist to attach GRADE to. | **M–L** |

### (d) Reporting & reproducibility

| Gap | What / why | Best-in-class + file | Effort |
|---|---|---|---|
| **Auto-generated Methods+Results text + Word report** | Turn numbers into prose ("random-effects MD 1.2, 95% CI 0.4–2.0, I²=63%, 12 studies") → DOCX/RTF. High-leverage, error-prone by hand. | **metafor `reporter()`** — one function writes a full narrative (model, heterogeneity, outlier/influence checks, funnel asymmetry) to HTML/PDF/Word via RMarkdown+pandoc, **APA refs included** → fills report text *and* citations at once. Wrap as "Export report". Template path: python-docx/Pandoc (both installed). | **M** (S for `reporter()` wrap) |
| **Reproducible R-script export** | Emit the exact `escalc()` + `rma()`/`metagen()`/`netmeta()` call with the user's params + a `read.csv` of their data + `sessionInfo()`. **A genuine differentiator — neither RevMan nor CMA does this.** Nearly free: you already build the call. | **JASP** `.maMakeMetaforCallText()` (`classicalmetaanalysiscommon.R:4201`): builds a **named-arg list**, pretty-prints native `metafor` call (runs in plain R, not JASP-internal). **MetaInsight** per-module `.Rmd` with `{{param}}` holes + `printVecAsis` to inline data. **jamovi** gets it structurally from manifest→R6 codegen. | **S–M** |
| **Citations / references output + RIS import** | Emit `citation()` for each package actually invoked + method key-refs; import RIS/BibTeX and map studies to keys (fits your Zotero+BBT workflow). | **jamovi** `refs:` field per results item + `00refs.yaml`; **JASP** `infoBottom` ref lists; **MetaInsight** `export_refPackages.R` (fixes the R-package bibtex `note→version` quirk). Python handles RIS/BibTeX; no R needed. | **S–M** |
| **Declarative results schema** | Add a symmetric *results* section to each manifest (typed table columns w/ number-format tokens like `zto`/`pvalue`, declared figures, text blocks, `refs`). One schema feeds both the results panel and the report exporter. | **jamovi** `metadv.r.yaml`. | **M** |

### (e) Interactive figures

| Gap | What / why | Best-in-class + file | Effort |
|---|---|---|---|
| **Forest column/order editor** | Controls panel: choose left-hand columns (title/width/align per column), study order, displayed statistics, scale, subgroup grouping — re-renders via existing R adapter. The pragmatic, well-scoped version of RevMan/CMA plot customization. | **JASP** `ForestPlotStudyInformation.qml` (per-column title/width/align) + `forestOrder` option. Avoid full WYSIWYG drag-canvas — low ROI since R produces the final vector. | **M** |
| **Interactive influence/outlier diagnostics** | Render Baujat/leverage/GOSH/influence scatter as **hover-to-identify** plots (plotly/mpld3) with a plain-language "how to read this" caption each. Yours are static today. | **MetaInsight** `bayes_deviance.R` (plotly dev-dev/stem/leverage) + `deviance_annotations` captions. Keep publication forest/funnel as vector. | **M** |
| **"Extend the call" escape hatch** | Optional validated "additional R args" box per analysis, spliced into the named-arg list — covers the long tail of `metafor` options without building UI for each. Composes with script export. | **JASP** `advancedExtendMetaforCall` (`ClassicalMetaAnalysisAdvanced.qml:510`). | **S** |

### (f) Analysis coverage still missing (thin adapters over installed packages)

| Add | Fills | Source | Effort |
|---|---|---|---|
| **`metafor::selmodel()`** (Vevea-Hedges step/beta/halfnorm selection models) | Publication-bias **sensitivity** — current weak spot (only trim-fill/PET-PEESE; DMAIR prefers selmodel, notes PET-PEESE overcorrects at k<20 or I²>80%). | metafor | **M** |
| **`dmetar::pcurve()` + `zcurve` package** | Evidential value / replicability (p-curve, z-curve EDR/ERR, R-index) — you asked for these. | dmetar / zcurve | **M** |
| **`dmetar::power.analysis()` (+subgroup)** | Meta-analytic power (none today). | dmetar | **S–M** |
| **`dmetar::find.outliers()` + `gosh.diagnostics()`** | *Interpret* your GOSH plot (k-means/DBSCAN/GMM clustering of the subset cloud). | dmetar | **M** |
| **`dmetar::multimodel.inference()`** | Model-averaged moderators + variable importance (beyond single meta-reg). | dmetar (glmulti over rma) | **M** |
| **`metafor::fsn()` + `tes()`** | Fail-safe N (Rosenthal/Orwin/Rosenberg) + test of excess significance — cheap bias completeness. | metafor | **S** |
| **`meta::read.rm5()` / `metacr()` / `metabind()`** | *Import* RevMan `.rm5`; template for your review-tree file + grouped forests. | meta | **M** |
| **`netmeta::decomp.design()` + `netcontrib()`** | NMA global consistency QC + contribution matrix (real CINeMA feed, upgrades your approx). | netmeta | **M** |
| **`dmetar::mlm.variance.distribution()`** | 3-level variance %-per-level + multilevel I² (QC for models you already fit). | dmetar | **S** |
| **`meta::drapery()`** | P-value-function QC visual exposing over-precision. | meta | **S** |

### (g) Validation / QC & trust

| Gap | What / why | Best-in-class + pattern | Effort |
|---|---|---|---|
| **Triangulated, guard-railed bias tab** | Never one test: **disable Egger at k<10**, refuse rare-event tests, run visual→asymmetry→correction→evidential-value and report **agreement across methods**. Directly serves the user's result-credibility rule. | `meta::metabias()` unifies Egger/Begg/Thompson/Peters/Harbord/Rücker and *refuses* tests when k/events too small. DMAIR pub-bias workflow. | **S–M** |
| **"Results health check" panel** | Auto-run outlier + Cook's + leave-one-out + heterogeneity bundle (τ², I², H², Q/df/p, prediction interval **together**) on every model; flag studies. | `metafor::reporter()` / `dmetar::InfluenceAnalysis()` run this by default. netmeta gates SUCRA/rankograms behind `decomp.design()`+`netsplit()`+`netheat()` — enforce that order in NMA UI. | **M** |
| **Typed validation chain on entry** | Study-named, actionable errors at data-entry time (see B1). | MetaInsight `ValidateUploadedData()`. | (in B1) |
| **Per-field help + conditional visibility + guided tour** | `info` tooltip per option/result; `visibleWhen`/`enabledWhen` predicates (Knapp-Hartung only for RE; trim-fill only for funnel methods); first-run product tour. Makes 61 analyses approachable and prevents misuse. | **JASP** `info:` on every control + `visible:`/`enabled:` bindings; **jamovi** `.u.yaml` `enable:` predicates; **MetaInsight** `core_intro.R` scripted `rintrojs` tour + per-module `.md` help + one-click **example datasets** (double as test fixtures). | **S–M** |
| **Reactive/cached recompute** | Declare per-output dependencies so flipping a plot color doesn't refit the model (matters as reviews grow). | **JASP** `$dependOn(...)`. Optional. | **M** |

---

## 3. What Meta Wingman ALREADY does better than RevMan/CMA (honest, short)

- **Statistical breadth neither has**: network meta-analysis, bivariate/HSROC diagnostic accuracy, TSA/sequential, dose-response splines, RVE/3-level, PET-PEESE, E-value. RevMan has *none* of these and CMA lacks most. RevMan has no meta-regression, trim-fill, Egger, or NMA in its GUI at all.
- **Local-only, data-never-leaves**: RevMan Web is cloud/Archie; you are private by design. (So real-time multi-author collaboration is a deliberate **non-goal**, not a gap — a git-friendly JSON `.mwproj` is the right substitute.)
- **PRISMA 2020** built-in (parity with RevMan's flow-diagram template).
- **Publication-spec vector figures** (Arial, PDF+PNG, Nature artwork spec) — matches/exceeds RevMan+CMA raster+vector output.
- **Free & open toolchain** vs CMA (closed, paid, Windows-only, tiered paywall) — your bias/subgroup/meta-reg tools are CMA-Professional-only features, given away.
- **Chinese-biomedical bilingual native UI** — neither competitor offers.

---

## 4. Phased roadmap (impact/effort, tuned to local single-dev, Chinese-biomedical)

**NEXT 3 — the backbone + cheapest differentiators (all S, mostly no R changes):**
1. **Project file `.mwproj`** (A1). Unblocks everything; copy MetaInsight's save/load-closure + version-stamp-gate pattern. **S.**
2. **Reproducible R-script export** (D2). Near-free — surface the call you already build (JASP named-arg-list technique). A differentiator CMA/RevMan lack; serves the user's reproducibility rule. **S.**
3. **`metafor::reporter()` "Export report" button** (D1) → Methods+Results prose + APA citations + Word/PDF in one wrap. Two gaps closed with one function; fits the LaTeX/Word delivery habit. **S–M.**

**THEN 5 — data quality + the review model:**
4. **In-app data grid + typed validator chain** (B1) with MetaInsight-style study-named messages. **M.**
5. **Effect-size wizard + `conv.fivenum/2x2/wald` converters** (B2/B-conv) — the median/IQR→mean/SD helper is the single most-requested extraction tool. **M.**
6. **Structured review tree** (C1) — the architectural centerpiece; depends on #1. **L.**
7. **RoB judgement entry UI** (RoB2/ROBINS-I/QUADAS-2 → existing robvis) (C-b). Cochrane table-stakes; a differentiator vs CMA/JASP/jamovi. **M.**
8. **selmodel + pcurve/zcurve + fsn/tes** bias/replicability additions (F) + guard-railed triangulated bias tab (G). Fixes the current pub-bias weak spot; serves credibility rule. **M.**

**LATER — composes on the tree, higher cost / narrower audience:**
9. **GRADE/SoF workflow** (C2) — build after the tree so outcomes exist to attach to. **M–L.**
10. **Global exclusion set → primary-vs-sensitivity everywhere** (A3) + **interactive hover diagnostics** (E2). **M each.**
11. **Forest column/order editor + extend-call escape hatch** (E1/E3). **M / S.**
12. **NMA consistency QC ordering** (`decomp.design`/`netcontrib`) + **multimodel inference** + **RevMan `.rm5` import** + **per-field help/tooltips/guided tour + example datasets** (G) sprinkled throughout. **S–M each.**

---

## 5. Licensing notes for code we'd port/adapt

- **MetaInsight — GPL-3.0.** **JASP `jaspMetaAnalysis` — R is GPL(≥2), QML files carry AGPL-3 headers.** **jamovi MAJOR — GPL-3.** All three are copyleft. **Reimplement the *patterns/architecture* (not copyrightable) in your own Python/R; do NOT paste their source** into Meta Wingman unless Wingman itself becomes GPL-compatible. This applies to every "file to learn from" cited above — read them, then write your own adapter.
- **MetaInsight bundled example datasets** (`inst/extdata`) are GPL-covered and derived from named published papers — if you ship example data, **cite the source study** and generate/curate your own rather than redistributing theirs.
- **Underlying engines are the legitimate dependency surface** and you already wrap them: `metafor` GPL(≥2), `meta`/`netmeta` GPL(≥2), `mada`, `metasens`, `robvis`, `dmetar`, `zcurve` — calling these from your adapters is fine and is the intended use. Emitting native `metafor`/`meta`/`netmeta` calls in the reproducible script (JASP's approach) is preferable to emitting Wingman-internal calls, both for reproducibility and to keep the license surface clean.
- **`metafor::reporter()` output** (RMarkdown → pandoc) is generated content, not ported source — no licensing constraint on the reports your users produce.
- Net: the entire plan is **deterministic and fully local** — no cloud service required, consistent with Wingman's privacy-by-design and the user's local-first constraint.