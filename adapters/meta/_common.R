## =====================================================================
## _common.R —— 所有 run_*.R 适配脚本共用的样板。
## 各脚本以  source(file.path(<自身目录>, "_common.R"))  载入。工具包本身不改。
## 提供:参数解析(args/getarg)、初始化(mw_init:定位+载入工具包)、
##       PDF→PNG(to_png)、取列(col_of/slab_of)、效应量(mw_escalc)。
## =====================================================================
args <- commandArgs(trailingOnly = TRUE)
getarg <- function(k, d = NA) { i <- which(args == paste0("--", k)); if (length(i) && i[1] < length(args)) args[i[1] + 1] else d }

## 读 input/outdir/toolkit + 基本校验 + 建输出目录 + 按 00→22 顺序 source 工具包(载入全部函数与 %||% 等依赖)。
## need_toolkit=FALSE 用于不依赖工具包的方法(如 dataprep_msd,仅用 estmeansd)。
mw_init <- function(need_input = TRUE, need_toolkit = TRUE) {
  input   <- getarg("input")
  outdir  <- getarg("outdir", "results")
  toolkit <- getarg("toolkit", Sys.getenv("META_TOOLKIT", unset = ""))
  if (need_input && is.na(input)) stop("需要 --input CSV")
  if (need_toolkit && (!nzchar(toolkit) || !dir.exists(file.path(toolkit, "R"))))
    stop("找不到 meta 工具包,请设 --toolkit <dir> 或环境变量 META_TOOLKIT")
  dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
  if (need_toolkit)
    for (f in sort(list.files(file.path(toolkit, "R"), pattern = "\\.R$", full.names = TRUE))) source(f)
  list(input = input, outdir = outdir, toolkit = toolkit)
}

## PDF → PNG(界面仅显示 PNG)
to_png <- function(pdf) { png <- sub("\\.pdf$", ".png", pdf)
  suppressWarnings(pdftools::pdf_convert(pdf, format = "png", dpi = 150, pages = 1, filenames = png, verbose = FALSE)); invisible(png) }

## 从 df 取列(--key 可覆盖列名),缺列即报错
col_of <- function(df, k, d) { v <- getarg(k, d); if (v %in% names(df)) df[[v]] else stop(sprintf("CSV 缺列 '%s'(参数 --%s)", v, k)) }

## 研究标签向量(--slab 指定列;缺则 Study 1..n)
slab_of <- function(df, slabcol) if (slabcol %in% names(df)) as.character(df[[slabcol]]) else paste("Study", seq_len(nrow(df)))

## 统一算效应量(二分类 / 连续 / 相关型);pairwise 与 influence 共用。
mw_escalc <- function(df, measure) {
  if (measure %in% c("OR", "RR", "RD", "PETO"))
    es <- metafor::escalc(measure = measure, ai = col_of(df, "ai", "ai"), bi = col_of(df, "bi", "bi"),
                          ci = col_of(df, "ci", "ci"), di = col_of(df, "di", "di"))
  else if (measure %in% c("SMD", "MD", "SMDH", "ROM"))
    es <- metafor::escalc(measure = measure, m1i = col_of(df, "m1i", "m1i"), sd1i = col_of(df, "sd1i", "sd1i"),
                          n1i = col_of(df, "n1i", "n1i"), m2i = col_of(df, "m2i", "m2i"),
                          sd2i = col_of(df, "sd2i", "sd2i"), n2i = col_of(df, "n2i", "n2i"))
  else if (measure %in% c("ZCOR", "COR"))
    es <- metafor::escalc(measure = measure, ri = col_of(df, "ri", "ri"), ni = col_of(df, "ni", "ni"))
  else stop(sprintf("本适配暂不支持 measure=%s(见 es_guide())", measure))
  as.data.frame(es)
}
