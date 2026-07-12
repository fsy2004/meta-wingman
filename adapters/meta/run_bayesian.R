## =====================================================================
## run_bayesian.R —— launcher 适配层:把 meta-analysis-toolkit 的贝叶斯
## 随机效应 meta(R/22_bayesian_meta.R 的 bma_run)暴露成 --input/--outdir
## 的 CLI 方法。工具包本身不改;此脚本 source 它、读用户 CSV(study,yi,sei)、
## 调 bma_run,出图(森林 + 后验密度 PDF→PNG 供界面显示)+ 汇总表。
##
## 用法:
##   Rscript run_bayesian.R --input bayesian.csv --outdir out \
##           --tau_prior halfnormal --tau_scale 0.5
##   工具包路径: --toolkit <dir> 或环境变量 META_TOOLKIT
##   输入 CSV 列: study(研究名), yi(各研究效应量,如 log-OR), sei(标准误)
## =====================================================================
suppressWarnings(suppressMessages({ library(bayesmeta); library(pdftools) }))
## 载入同目录公共样板(getarg / mw_init / to_png / slab_of)
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])), "_common.R"))

init <- mw_init(); input <- init$input; outdir <- init$outdir
tau_prior <- tolower(getarg("tau_prior", "halfnormal"))
tau_scale <- as.numeric(getarg("tau_scale", "0.5"))
slabcol   <- getarg("slab", "study")

## ---- 读数据(直接给定 yi,sei;这是贝叶斯 normal-normal 模型的输入)----
df <- mw_read_csv(input)
if (!all(c("yi", "sei") %in% names(df))) stop("CSV 需含列 yi(效应量)与 sei(标准误)")
slab_vec <- slab_of(df, slabcol)
cat(sprintf("Step 1/3: 读入 %d 个研究,tau 先验 = %s(scale=%.3g)\n", nrow(df), tau_prior, tau_scale))

## ---- 贝叶斯随机效应 meta(工具包 bma_run;out_prefix 指向 <outdir>/bma)----
cat("Step 2/3: 贝叶斯合并(bayesmeta,后验 mu/tau + 预测区间)...\n")
out_prefix <- file.path(outdir, "bma")
res <- bma_run(df$yi, df$sei, labels = slab_vec,
               tau_prior = tau_prior, tau_scale = tau_scale, out_prefix = out_prefix)

## ---- PDF(森林 + 后验密度)→ PNG + 汇总表 ----
cat("Step 3/3: 转 PNG + 写汇总表...\n")
for (pdf in c(paste0(out_prefix, "_forest.pdf"), paste0(out_prefix, "_posterior.pdf")))
  if (file.exists(pdf)) to_png(pdf)
write.csv(res$row, file.path(outdir, "bma_summary.csv"), row.names = FALSE)

cat(sprintf("完成。森林图 + 后验密度图 + 汇总表写入 %s\n", outdir))
