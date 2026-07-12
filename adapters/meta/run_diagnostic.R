## =====================================================================
## run_diagnostic.R —— launcher 适配层:把 meta-analysis-toolkit 的函数库
## 暴露成 --input/--outdir 的 CLI 方法(诊断试验准确性 DTA / SROC 分析)。
## 工具包本身不改;此脚本 source 它、读用户 CSV、调 dta_run(双变量
## Reitsma 模型),出图(PDF→PNG 供界面显示)+ 汇总表。
##
## 用法:
##   Rscript run_diagnostic.R --input diagnostic.csv --outdir out \
##           --study study --add_correction 0.5
##   工具包路径: --toolkit <dir> 或环境变量 META_TOOLKIT
## 数据: 每行一个研究,2x2 诊断表列 TP,FN,FP,TN(+ 研究名列,默认 study)。
## =====================================================================
suppressWarnings(suppressMessages({ library(mada); library(pdftools) }))

args <- commandArgs(trailingOnly = TRUE)
getarg <- function(k, d = NA) { i <- which(args == paste0("--", k)); if (length(i) && i[1] < length(args)) args[i[1] + 1] else d }

input    <- getarg("input")
outdir   <- getarg("outdir", "results")
toolkit  <- getarg("toolkit", Sys.getenv("META_TOOLKIT", unset = ""))
studycol <- getarg("study", "study")
add_corr <- as.numeric(getarg("add_correction", "0.5"))

if (is.na(input)) stop("需要 --input CSV")
if (!nzchar(toolkit) || !dir.exists(file.path(toolkit, "R")))
  stop("找不到 meta 工具包,请设 --toolkit <dir> 或环境变量 META_TOOLKIT")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

## ---- source 工具包(00→22 顺序,依赖 %||% 等)----
for (f in sort(list.files(file.path(toolkit, "R"), pattern = "\\.R$", full.names = TRUE))) source(f)

## ---- 读数据 ----
df <- read.csv(input, check.names = FALSE, stringsAsFactors = FALSE)
need <- c("TP", "FN", "FP", "TN")
if (!all(need %in% names(df)))
  stop(sprintf("CSV 缺列:需要 %s(每行一个研究的 2x2 诊断表)", paste(need, collapse = ", ")))
cat(sprintf("Step 1/3: 读入 %d 个诊断研究(TP/FN/FP/TN)\n", nrow(df)))

## 研究名 -> 作为数据框行名,便于森林图标注每个研究
dat <- df[, need]
if (studycol %in% names(df)) rownames(dat) <- make.unique(as.character(df[[studycol]]))

## ---- 双变量 DTA 合并(工具包 dta_run:Reitsma 模型 + SROC + 森林)----
cat("Step 2/3: 双变量随机效应合并(Reitsma / HSROC)+ SROC 曲线...\n")
prefix <- file.path(outdir, "dta")
res <- dta_run(dat, out_prefix = prefix, add_correction = add_corr)

## ---- PDF → PNG(SROC + 敏感度森林 + 特异度森林)----
to_png <- function(pdf) { png <- sub("\\.pdf$", ".png", pdf)
  suppressWarnings(pdftools::pdf_convert(pdf, format = "png", dpi = 150, pages = 1, filenames = png, verbose = FALSE)); invisible(png) }
cat("Step 3/3: 出图(SROC + 森林)转 PNG + 汇总表...\n")
for (pdf in sort(list.files(outdir, pattern = "\\.pdf$", full.names = TRUE))) to_png(pdf)

## ---- 汇总表(合并操作点 + 似然比 + DOR + AUC)----
co  <- res$summary$coefficients
sens <- res$sensitivity; spec <- res$specificity
lr  <- res$likelihood_ratios_DOR
summ <- data.frame(
  metric = c("Sensitivity", "Specificity", "SROC AUC", "posLR", "negLR", "DOR"),
  estimate = c(sens, spec, res$auc$AUC,
               lr["posLR", "Median"], lr["negLR", "Median"], lr["DOR", "Median"])
)
write.csv(summ, file.path(outdir, "dta_summary.csv"), row.names = FALSE)

cat(sprintf("完成。SROC + 森林图 + 汇总表写入 %s\n", outdir))
