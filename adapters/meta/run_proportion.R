## =====================================================================
## run_proportion.R —— launcher 适配层:把 meta-analysis-toolkit 的单臂
## 比例(prevalence/proportion)meta 分析暴露成 --input/--outdir 的 CLI 方法。
## 工具包本身不改;此脚本 source 它、读用户 CSV、调 ma_proportion,
## 出比例森林图(PDF→PNG 供界面显示)+ 汇总表。
##
## 用法:
##   Rscript run_proportion.R --input proportion.csv --outdir out \
##           --event xi --n ni --studlab study --method PFT
##   工具包路径: --toolkit <dir> 或环境变量 META_TOOLKIT
## =====================================================================
suppressWarnings(suppressMessages({ library(meta); library(metafor); library(pdftools) }))
## 载入同目录公共样板(getarg / mw_init / to_png / slab_of)
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])), "_common.R"))

init <- mw_init(); input <- init$input; outdir <- init$outdir
eventc  <- getarg("event", "xi")
nc      <- getarg("n", "ni")
slabcol <- getarg("studlab", "study")
method  <- toupper(getarg("method", "PFT"))

## ---- 读数据 ----
df <- read.csv(input, check.names = FALSE, stringsAsFactors = FALSE)
cat(sprintf("Step 1/3: 读入 %d 个研究,method = %s\n", nrow(df), method))
col <- function(nm) { if (nm %in% names(df)) df[[nm]] else stop(sprintf("CSV 缺列 '%s'", nm)) }
event_v <- col(eventc)
n_v     <- col(nc)
slab_v  <- slab_of(df, slabcol)

## ---- 单臂比例 meta(工具包 ma_proportion;随机效应 REML + 预测区间)----
## 传向量(data = NULL 路径):NSE 解析器直接求值这些向量。
cat("Step 2/3: 随机效应比例合并 + 森林图...\n")
f_forest <- file.path(outdir, "forest.pdf")
res <- ma_proportion(event = event_v, n = n_v, studlab = slab_v, method = method, out = f_forest)
to_png(f_forest)
print(res$row)

## ---- 汇总表(自然比例尺度:合并比例 + 95%CI + 预测区间 + 异质性)----
cat("Step 3/3: 写出汇总表...\n")
write.csv(res$row, file.path(outdir, "summary.csv"), row.names = FALSE)

cat(sprintf("完成。比例森林图 + 汇总表写入 %s\n", outdir))
