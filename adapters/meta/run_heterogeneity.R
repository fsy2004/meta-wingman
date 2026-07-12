## =====================================================================
## run_heterogeneity.R —— launcher 适配层:把 meta-analysis-toolkit 的
## 异质性分析(亚组 + Meta 回归)暴露成 --input/--outdir 的 CLI 方法。
## 工具包本身不改;此脚本 source 它、读用户 CSV、先拟合配对模型(escalc +
## ma_pairwise, 二分类 OR),再调 ma_subgroup(按类别调节变量分亚组)与
## ma_metareg(按连续调节变量做 meta 回归 + 气泡图)。
## 亚组结果打进日志并写 CSV;meta 回归系数表写 CSV,气泡图 PDF→PNG 供界面显示。
##
## 用法:
##   Rscript run_heterogeneity.R --input heterogeneity.csv --outdir out \
##           --measure OR --subgroup alloc --moderator ablat
##   工具包路径: --toolkit <dir> 或环境变量 META_TOOLKIT
## 输入 CSV: 每行一个研究,需列 ai,bi,ci,di + 研究名列(默认 study)
##           + 一个类别调节列(默认 alloc) + 一个数值调节列(默认 ablat)。
## =====================================================================
suppressWarnings(suppressMessages({ library(metafor); library(meta); library(pdftools) }))
## 载入同目录公共样板(getarg / mw_init / to_png / col_of)
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])), "_common.R"))

init <- mw_init(); input <- init$input; outdir <- init$outdir
measure   <- toupper(getarg("measure", "OR"))
slabcol   <- getarg("slab", "study")
subgroup  <- getarg("subgroup", "alloc")
moderator <- getarg("moderator", "ablat")
method    <- getarg("method", "REML")
knha      <- tolower(getarg("knha", "true")) %in% c("true", "1", "yes", "t")

## ---- 读数据 + 算效应量(二分类 2x2 -> OR)----
df <- read.csv(input, check.names = FALSE, stringsAsFactors = FALSE)
cat(sprintf("Step 1/5: 读入 %d 个研究,measure = %s;亚组 = %s,调节变量 = %s\n",
            nrow(df), measure, subgroup, moderator))

if (measure %in% c("OR", "RR", "RD", "PETO")) {
  ai <- col_of(df, "ai", "ai"); bi <- col_of(df, "bi", "bi")   # escalc 外先解析,缺列清晰报错
  ci <- col_of(df, "ci", "ci"); di <- col_of(df, "di", "di")
  es <- metafor::escalc(measure = measure, ai = ai, bi = bi, ci = ci, di = di)
} else stop(sprintf("本适配的异质性分析针对二分类 2x2(measure=OR/RR/RD/PETO),收到 measure=%s", measure))

es <- as.data.frame(es)
## 把研究级调节变量并入 es,供 ma_subgroup / ma_metareg 从 fit$es 读取
if (!subgroup %in% names(df))  stop(sprintf("CSV 缺亚组列 '%s'(参数 --subgroup)", subgroup))
if (!moderator %in% names(df)) stop(sprintf("CSV 缺调节列 '%s'(参数 --moderator)", moderator))
es[[subgroup]]  <- df[[subgroup]]
es[[moderator]] <- df[[moderator]]
if (slabcol %in% names(df)) es[[slabcol]] <- df[[slabcol]]

## ---- 先拟合配对随机效应模型(REML + Knapp-Hartung),得 ma_fit ----
cat("Step 2/5: 拟合随机效应基线模型...\n")
fit <- ma_pairwise(es, measure = measure, method = method, knha = knha)
print(fit)

## ---- 亚组分析(类别调节变量;打印 + 写表)----
cat(sprintf("Step 3/5: 亚组分析(按 '%s')...\n", subgroup))
sg <- ma_subgroup(fit, subgroup)
write.csv(sg$table, file.path(outdir, "subgroup.csv"), row.names = FALSE)
write.csv(as.data.frame(sg$qm), file.path(outdir, "subgroup_Qtest.csv"), row.names = FALSE)

## ---- Meta 回归(连续调节变量;系数表 + 气泡图 PDF)----
cat(sprintf("Step 4/5: Meta 回归(~ %s)+ 气泡图...\n", moderator))
mods_f <- as.formula(paste0("~", moderator))
f_reg  <- file.path(outdir, "metareg.pdf")
mr <- ma_metareg(fit, mods_f, out = f_reg)
write.csv(mr$coef, file.path(outdir, "metareg_coef.csv"), row.names = FALSE)

## ---- PDF -> PNG(供界面显示)----
cat("Step 5/5: 气泡图 PDF -> PNG...\n")
if (file.exists(f_reg)) to_png(f_reg) else cat("  (未生成气泡图:调节变量非单一连续型,已跳过)\n")

cat(sprintf("完成。亚组表/回归系数表 + 气泡图写入 %s\n", outdir))
