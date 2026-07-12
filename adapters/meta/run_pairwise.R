## =====================================================================
## run_pairwise.R —— launcher 适配层:把 meta-analysis-toolkit 的函数库
## 暴露成 --input/--outdir 的 CLI 方法(配对 meta 分析)。
## 工具包本身不改;此脚本 source 它、读用户 CSV、调 ma_pairwise/森林/漏斗,
## 出图(PDF→PNG 供界面显示)+ 汇总表。
##
## 用法:
##   Rscript run_pairwise.R --input studies.csv --outdir out --measure OR \
##           --ai ai --bi bi --ci ci --di di --slab study --method REML --knha true
##   连续型: --measure SMD --m1i m1 --sd1i sd1 --n1i n1 --m2i m2 --sd2i sd2 --n2i n2
##   工具包路径: --toolkit <dir> 或环境变量 META_TOOLKIT
## =====================================================================
suppressWarnings(suppressMessages({ library(metafor); library(meta); library(pdftools) }))

args <- commandArgs(trailingOnly = TRUE)
getarg <- function(k, d = NA) { i <- which(args == paste0("--", k)); if (length(i) && i[1] < length(args)) args[i[1] + 1] else d }

input   <- getarg("input")
outdir  <- getarg("outdir", "results")
toolkit <- getarg("toolkit", Sys.getenv("META_TOOLKIT", unset = ""))
measure <- toupper(getarg("measure", "OR"))
slabcol <- getarg("slab", "study")
method  <- getarg("method", "REML")
knha    <- tolower(getarg("knha", "true")) %in% c("true", "1", "yes", "t")

if (is.na(input)) stop("需要 --input CSV")
if (!nzchar(toolkit) || !dir.exists(file.path(toolkit, "R")))
  stop("找不到 meta 工具包,请设 --toolkit <dir> 或环境变量 META_TOOLKIT")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

## ---- source 工具包(00→22 顺序)----
for (f in sort(list.files(file.path(toolkit, "R"), pattern = "\\.R$", full.names = TRUE))) source(f)

## ---- 读数据 + 算效应量(用向量调 escalc,稳)----
df <- read.csv(input, check.names = FALSE, stringsAsFactors = FALSE)
cat(sprintf("Step 1/4: 读入 %d 个研究,measure = %s\n", nrow(df), measure))
col <- function(k, d) { v <- getarg(k, d); if (v %in% names(df)) df[[v]] else stop(sprintf("CSV 缺列 '%s'(参数 --%s)", v, k)) }

if (measure %in% c("OR", "RR", "RD", "PETO")) {
  es <- metafor::escalc(measure = measure, ai = col("ai","ai"), bi = col("bi","bi"),
                        ci = col("ci","ci"), di = col("di","di"))
} else if (measure %in% c("SMD", "MD", "SMDH", "ROM")) {
  es <- metafor::escalc(measure = measure, m1i = col("m1i","m1i"), sd1i = col("sd1i","sd1i"),
                        n1i = col("n1i","n1i"), m2i = col("m2i","m2i"), sd2i = col("sd2i","sd2i"), n2i = col("n2i","n2i"))
} else if (measure %in% c("ZCOR", "COR")) {
  es <- metafor::escalc(measure = measure, ri = col("ri","ri"), ni = col("ni","ni"))
} else stop(sprintf("本适配暂不支持 measure=%s(见 es_guide())", measure))

es <- as.data.frame(es)
slab_vec <- if (slabcol %in% names(df)) as.character(df[[slabcol]]) else paste("Study", seq_len(nrow(df)))

## ---- 配对 meta(工具包 ma_pairwise,顶刊默认:REML + Knapp-Hartung + 预测区间)----
cat("Step 2/4: 随机效应合并...\n")
fit <- ma_pairwise(es, measure = measure, method = method, knha = knha)
print(fit)

## ---- 出图:森林 + 漏斗(PDF)→ 转 PNG ----
to_png <- function(pdf) { png <- sub("\\.pdf$", ".png", pdf)
  suppressWarnings(pdftools::pdf_convert(pdf, format = "png", dpi = 150, pages = 1, filenames = png, verbose = FALSE)); invisible(png) }
cat("Step 3/4: 森林图 + 漏斗图...\n")
## slab 直接传给 ma_forest -> metafor::forest 的 slab 参数(显示研究标签)
f_forest <- file.path(outdir, "forest.pdf"); ma_forest(fit, f_forest, slab = slab_vec); to_png(f_forest)
f_funnel <- file.path(outdir, "funnel.pdf"); ma_funnel(fit, f_funnel); to_png(f_funnel)

## ---- 发表偏倚文字报告(进日志)+ 汇总表 ----
cat("Step 4/4: 发表偏倚检验 + 汇总表...\n")
invisible(tryCatch(ma_pubbias(fit), error = function(e) cat("  (发表偏倚: ", conditionMessage(e), ")\n", sep = "")))
write.csv(ma_summary_row(fit, "pooled"), file.path(outdir, "summary.csv"), row.names = FALSE)

cat(sprintf("完成。森林/漏斗图 + 汇总表写入 %s\n", outdir))
