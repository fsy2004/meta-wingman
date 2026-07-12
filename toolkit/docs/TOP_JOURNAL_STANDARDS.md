# Top-journal standards → toolkit coverage

What high-impact journals and the reporting guidelines expect from a meta-analysis,
and where this toolkit delivers it. The goal: nothing a reviewer asks for is missing.

## PRISMA 2020 (Page 2021) — reporting a systematic review

| PRISMA item | Requirement | Toolkit |
|-------------|-------------|---------|
| 16a / Fig 1 | Study selection **flow diagram** with counts at each stage | `prisma_flow()` (R/08) |
| 20a | **Forest plot** of each synthesis | `ma_forest()` (R/06) |
| 20b–20d | Pooled effect, CI, heterogeneity (I², τ²) | `ma_pairwise()` / `ma_summary_row()` (R/02) |
| 21 | **Publication bias** across studies | `ma_pubbias()`, `ma_funnel()` (R/04) |
| 19 / 22 | **Risk of bias** per study & across studies; certainty | `rob_traffic()`/`rob_summary()` (R/09), `ma_grade()` (R/07) |
| 20d | **Sensitivity / robustness** analyses | `ma_influence()` (R/05), sensitivity via `ma_pairwise()` on subsets |
| 20c | Subgroups & meta-regression of heterogeneity | `ma_subgroup()`, `ma_metareg()` (R/03) |
| — | **Prediction interval** (increasingly required) | reported by `ma_pairwise()` (R/02) |

## Cochrane Handbook — analysis expectations

| Expectation | Toolkit |
|-------------|---------|
| Random-effects with an appropriate τ² estimator (REML) | `ma_pairwise(method="REML")` |
| Hartung-Knapp adjustment for the pooled CI | `ma_pairwise(knha=TRUE)` (default) |
| Handling medians/ranges/SE (RevMan-style conversions) | `R/00_data_prep.R` (Wan 2014, estmeansd) |
| I², τ², Cochran's Q, H² reported | `ma_pairwise()` / `ma_summary_row()` |
| Funnel plot only when k ≥ 10; Egger with caveats | `ma_pubbias(min_k=10)` warns below threshold |
| GRADE certainty per outcome + Summary-of-Findings table | `ma_grade()`, `ma_sof_table()` (R/07) |

## GRADE — certainty of evidence

Start High (RCT) / Low (observational); five downgrade domains (risk of bias,
inconsistency, indirectness, imprecision, publication bias) and three upgrade
domains for observational data. `ma_grade()` implements the algebra; `ma_grade_suggest()`
offers heuristic starting points (imprecision from CI, inconsistency from I²) that the
reviewer must confirm — it never auto-finalises certainty.

## MOOSE (Stroup 2000) — observational meta-analyses

Reporting-focused; the analysis pieces (effect pooling, heterogeneity exploration via
subgroup/meta-regression, sensitivity and small-study analyses) are all covered by
R/02–R/05. Certainty via GRADE for observational bodies of evidence (R/07).

## Beyond pairwise (advanced designs)

| Design | Standard | Toolkit |
|--------|----------|---------|
| **Network meta-analysis** | PRISMA-NMA (Hutton 2015); network graph, league table, ranking (P-score/SUCRA), consistency (node-splitting) | `nma_run()`, `nma_graph()`, `nma_league()`, `nma_rank()`, `nma_inconsistency()` (R/20) |
| **Diagnostic test accuracy** | Cochrane DTA; bivariate/HSROC model, SROC curve, pooled sensitivity/specificity/DOR | `dta_run()` (R/21) |
| **Bayesian meta-analysis** | Weakly-informative heterogeneity prior; credible + prediction intervals; shrinkage | `bma_run()` (R/22) |

## Figures — publication conventions

The toolkit's figures are the ones editors expect and are drawn as vector PDFs:
forest, contour-enhanced funnel, Baujat, leave-one-out, cumulative, drapery,
bubble meta-regression, SROC, network graph, rankogram, posterior densities, and the
Cochrane risk-of-bias traffic-light. Plain bar charts are avoided by design (the sole
exception is the Cochrane weighted RoB summary bar, which is itself a reporting standard).
