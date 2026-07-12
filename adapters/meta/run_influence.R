## =====================================================================
## run_influence.R —— launcher 适配层:把 meta-analysis-toolkit 的
## 影响分析 / 稳健性诊断(05_influence.R)暴露成 --input/--outdir 的
## CLI 方法。工具包本身不改;此脚本 source 它、读用户 CSV、先拟合
## 随机效应模型(照 run_pairwise 的 ma_pairwise),再调 ma_influence,
## 出多张影响诊断图(留一法 LOO / Baujat / 累积 / GOSH,PDF→PNG 供
## 界面显示)+ 三张诊断表(留一 / 案例删除影响 / 累积)。
##
## 用法:
##   Rscript run_influence.R --input studies.csv --outdir out --measure OR \
##           --ai ai --bi bi --ci ci --di di --slab study --method REML --knha true
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
attr(es, "slab") <- slab_vec   ## ma_influence 从 attr(es,'slab') 恢复研究标签

## ---- 拟合随机效应模型(工具包 ma_pairwise,顶刊默认:REML + Knapp-Hartung)----
cat("Step 2/4: 随机效应合并(拟合待诊断模型)...\n")
fit <- ma_pairwise(es, measure = measure, method = method, knha = knha)

## ---- 影响 / 稳健性诊断(工具包 ma_influence)----
## out_prefix 生成: <prefix>_baujat.pdf / _loo.pdf / _cumulative.pdf / (k<=20)_gosh.pdf
cat("Step 3/4: 影响分析(留一法 / Baujat / 累积 / GOSH)...\n")
inf <- ma_influence(fit, out_prefix = file.path(outdir, "inf"))

## ---- 批量把 outdir 里所有 PDF 转 PNG(界面显示)----
cat("Step 4/4: PDF → PNG + 诊断表...\n")
pdfs <- sort(list.files(outdir, pattern = "\\.pdf$", full.names = TRUE))
for (pdf in pdfs) {
  png <- sub("\\.pdf$", ".png", pdf)
  suppressWarnings(pdftools::pdf_convert(pdf, format = "png", dpi = 150, pages = 1, filenames = png, verbose = FALSE))
  cat(sprintf("  %s\n", basename(png)))
}

## ---- 诊断表(留一 / 案例删除影响 / 累积)----
write.csv(inf$loo,        file.path(outdir, "leave_one_out.csv"), row.names = FALSE)
write.csv(inf$influence,  file.path(outdir, "influence_diag.csv"), row.names = FALSE)
write.csv(inf$cumulative, file.path(outdir, "cumulative.csv"),    row.names = FALSE)

cat(sprintf("完成。影响分析图(%d 张)+ 3 张诊断表写入 %s\n", length(pdfs), outdir))
