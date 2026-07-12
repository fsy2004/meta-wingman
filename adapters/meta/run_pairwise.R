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
## 载入同目录公共样板(getarg / mw_init / to_png / col_of / mw_escalc)
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])), "_common.R"))

init <- mw_init(); input <- init$input; outdir <- init$outdir
measure <- toupper(getarg("measure", "OR"))
slabcol <- getarg("slab", "study")
method  <- getarg("method", "REML")
knha    <- tolower(getarg("knha", "true")) %in% c("true", "1", "yes", "t")

## ---- 读数据 + 算效应量 ----
df <- mw_read_csv(input)
cat(sprintf("Step 1/4: 读入 %d 个研究,measure = %s\n", nrow(df), measure))
es <- mw_escalc(df, measure)
slab_vec <- slab_of(df, slabcol)

## ---- 配对 meta(工具包 ma_pairwise,顶刊默认:REML + Knapp-Hartung + 预测区间)----
cat("Step 2/4: 随机效应合并...\n")
fit <- ma_pairwise(es, measure = measure, method = method, knha = knha)
print(fit)

## ---- 出图:森林 + 漏斗(PDF)→ 转 PNG ----
cat("Step 3/4: 森林图 + 漏斗图...\n")
f_forest <- file.path(outdir, "forest.pdf"); ma_forest(fit, f_forest, slab = slab_vec); to_png(f_forest)
f_funnel <- file.path(outdir, "funnel.pdf"); ma_funnel(fit, f_funnel); to_png(f_funnel)

## ---- 发表偏倚文字报告(进日志)+ 汇总表 ----
cat("Step 4/4: 发表偏倚检验 + 汇总表...\n")
invisible(tryCatch(ma_pubbias(fit), error = function(e) cat("  (发表偏倚: ", conditionMessage(e), ")\n", sep = "")))
write.csv(ma_summary_row(fit, "pooled"), file.path(outdir, "summary.csv"), row.names = FALSE)

cat(sprintf("完成。森林/漏斗图 + 汇总表写入 %s\n", outdir))
