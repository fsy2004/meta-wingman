## =====================================================================
## run_network.R —— launcher 适配层:把 meta-analysis-toolkit 的函数库
## 暴露成 --input/--outdir 的 CLI 方法(网络 Meta 分析 / NMA)。
## 工具包本身不改;此脚本 source 它、读用户 CSV、调 nma_run + 网络图/
## rankogram/netsplit + league 表,出图(PDF→PNG 供界面显示)+ league.csv。
##
## 用法:
##   Rscript run_network.R --input network.csv --outdir out \
##           --format contrast --sm MD --reference plac --small_values desirable
##   对比格式(默认): CSV 需列 studlab, treat1, treat2, TE, seTE
##   臂格式: --format arm(需 studlab, treat + 二分类 event,n 或连续 n,mean,sd)
##   工具包路径: --toolkit <dir> 或环境变量 META_TOOLKIT
## =====================================================================
suppressWarnings(suppressMessages({ library(netmeta); library(meta); library(pdftools) }))

args <- commandArgs(trailingOnly = TRUE)
getarg <- function(k, d = NA) { i <- which(args == paste0("--", k)); if (length(i) && i[1] < length(args)) args[i[1] + 1] else d }

input        <- getarg("input")
outdir       <- getarg("outdir", "results")
toolkit      <- getarg("toolkit", Sys.getenv("META_TOOLKIT", unset = ""))
format       <- tolower(getarg("format", "contrast"))
sm           <- toupper(getarg("sm", "MD"))
reference    <- getarg("reference", "plac")
small_values <- tolower(getarg("small_values", "desirable"))

if (is.na(input)) stop("需要 --input CSV")
if (!nzchar(toolkit) || !dir.exists(file.path(toolkit, "R")))
  stop("找不到 meta 工具包,请设 --toolkit <dir> 或环境变量 META_TOOLKIT")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

## ---- source 工具包(00→22 顺序,载入 %||% 等依赖)----
for (f in sort(list.files(file.path(toolkit, "R"), pattern = "\\.R$", full.names = TRUE))) source(f)

## ---- 读数据 ----
df <- read.csv(input, check.names = FALSE, stringsAsFactors = FALSE)
cat(sprintf("Step 1/5: 读入 %d 行(format=%s, sm=%s, reference=%s)\n",
            nrow(df), format, sm, reference))

## ---- 拟合网络 Meta(工具包 nma_run;★按 format 转发对应列名,否则 arm 格式必崩)----
cat("Step 2/5: 拟合频率学派网络 Meta 模型...\n")
nma_args <- list(data = df, format = format, sm = sm, studlab = getarg("studlab", "studlab"))
if (format == "arm") {                       # 臂格式:转发 treat + (event,n) 或 (n,mean,sd),按列名自动侦测
  cols <- names(df)
  nma_args$treat <- getarg("treat", "treat")
  ev <- getarg("event", if ("event" %in% cols) "event" else NA)
  mm <- getarg("mean",  if ("mean"  %in% cols) "mean"  else NA)
  ss <- getarg("sd",    if ("sd"    %in% cols) "sd"    else NA)
  nn <- getarg("n",     if ("n"     %in% cols) "n"     else NA)
  if (!is.na(ev)) nma_args$event <- ev
  if (!is.na(mm)) nma_args$mean  <- mm
  if (!is.na(ss)) nma_args$sd    <- ss
  if (!is.na(nn)) nma_args$n     <- nn
  nma_args$allstudies <- TRUE
  treats <- unique(as.character(df[[nma_args$treat]]))
} else {                                     # 对比格式
  nma_args$treat1 <- getarg("treat1", "treat1"); nma_args$treat2 <- getarg("treat2", "treat2")
  nma_args$TE <- getarg("TE", "TE"); nma_args$seTE <- getarg("seTE", "seTE")
  treats <- unique(c(as.character(df[[nma_args$treat1]]), as.character(df[[nma_args$treat2]])))
}
## 参考处理不在数据中会让 netmeta 崩 → 回退到 netmeta 默认参考
nma_args$reference <- if (nzchar(reference) && reference %in% treats) reference else ""
if (nzchar(reference) && !(reference %in% treats))
  cat(sprintf("  (参考处理 '%s' 不在数据中,改用 netmeta 默认参考)\n", reference))
net <- do.call(nma_run, nma_args)
print(net)

## ---- PDF -> PNG 辅助 ----
to_png <- function(pdf) { png <- sub("\\.pdf$", ".png", pdf)
  suppressWarnings(pdftools::pdf_convert(pdf, format = "png", dpi = 150, pages = 1, filenames = png, verbose = FALSE)); invisible(png) }

## ---- 网络图 ----
cat("Step 3/5: 网络几何图(netgraph)...\n")
f_graph <- file.path(outdir, "netgraph.pdf"); nma_graph(net, f_graph); to_png(f_graph)

## ---- P-score 排名 + 累积 rankogram ----
cat("Step 4/5: P-score 排名 + rankogram...\n")
f_rank <- file.path(outdir, "rankogram.pdf")
rank_tab <- nma_rank(net, small.values = small_values, out = f_rank); to_png(f_rank)
write.csv(rank_tab, file.path(outdir, "pscore_ranking.csv"), row.names = FALSE)

## ---- 节点分割一致性检验 + league 表 ----
## 用工具包 nma_inconsistency() 计算 SIDE 节点分割对象;渲染在此完成:
## 本 netmeta 版本的 plot.netsplit 返回需显式 print() 的对象,故不走
## 其 out= 出图路径,改用 print(plot(ns)),失败回退 meta::forest(ns)。
cat("Step 5/5: 节点分割一致性(netsplit)+ league 联赛表...\n")
ns <- nma_inconsistency(net)
f_split <- file.path(outdir, "netsplit.pdf")
mw_pdf(f_split, width = 8, height = 8)
ok <- tryCatch({ print(graphics::plot(ns)); TRUE },
               error = function(e) tryCatch({ meta::forest(ns); TRUE }, error = function(e2) FALSE))
grDevices::dev.off()
if (ok) to_png(f_split) else cat("  (netsplit 图渲染失败, 跳过)\n")
nma_league(net, out = file.path(outdir, "league.csv"))

cat(sprintf("完成。网络图/rankogram/netsplit + league.csv + P-score 排名写入 %s\n", outdir))
