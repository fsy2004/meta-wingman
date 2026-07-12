## =====================================================================
## run_prisma.R —— launcher 适配层:把 meta-analysis-toolkit 的
## prisma_flow() 暴露成 --input/--outdir 的 CLI 方法(PRISMA 2020 流程图)。
## 工具包本身不改;此脚本 source 它、读用户 CSV(长表 field,subkey,value),
## 解析回 counts 具名 list、调 prisma_flow(),出 PDF→PNG。
##
## 用法:
##   Rscript run_prisma.R --input prisma.csv --outdir out --toolkit <dir>
##   可选: --cex 0.8(字号)
##
## 输入 CSV(三列 field,subkey,value):
##   标量字段(n_duplicates/n_screened/n_excluded_screen/n_fulltext_sought/
##            n_fulltext_notretrieved/n_fulltext_assessed/n_included_studies/
##            n_included_reports)—— subkey 留空,单行。
##   具名向量字段:
##     n_identified —— 各数据库(subkey=库名, value=命中数),多行。
##     n_fulltext_excluded —— 各排除原因(subkey=原因, value=篇数),多行。
##   工具包路径: --toolkit <dir> 或环境变量 META_TOOLKIT
## =====================================================================
suppressWarnings(suppressMessages({ library(pdftools) }))

args <- commandArgs(trailingOnly = TRUE)
getarg <- function(k, d = NA) { i <- which(args == paste0("--", k)); if (length(i) && i[1] < length(args)) args[i[1] + 1] else d }

input   <- getarg("input")
outdir  <- getarg("outdir", "results")
toolkit <- getarg("toolkit", Sys.getenv("META_TOOLKIT", unset = ""))
cex     <- as.numeric(getarg("cex", "0.8"))

if (is.na(input)) stop("需要 --input CSV")
if (!nzchar(toolkit) || !dir.exists(file.path(toolkit, "R")))
  stop("找不到 meta 工具包,请设 --toolkit <dir> 或环境变量 META_TOOLKIT")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

## ---- source 工具包(00→22 顺序,含 %||% 等依赖)----
for (f in sort(list.files(file.path(toolkit, "R"), pattern = "\\.R$", full.names = TRUE))) source(f)

## ---- 读长表并解析回 counts 具名 list ----
df <- read.csv(input, check.names = FALSE, stringsAsFactors = FALSE)
need <- c("field", "value")
if (!all(need %in% names(df))) stop("CSV 需含列: field, value(可选 subkey)")
if (!"subkey" %in% names(df)) df$subkey <- ""
df$subkey[is.na(df$subkey)] <- ""
cat(sprintf("Step 1/3: 读入 %d 行 PRISMA 计数\n", nrow(df)))

## 具名向量字段(多行 + subkey);其余按标量取单值
vec_fields <- c("n_identified", "n_fulltext_excluded")
counts <- list()
for (fld in unique(df$field)) {
  sub <- df[df$field == fld, , drop = FALSE]
  vals <- as.integer(sub$value)
  if (fld %in% vec_fields && any(nzchar(sub$subkey))) {
    names(vals) <- sub$subkey
    counts[[fld]] <- vals
  } else {
    counts[[fld]] <- vals[1]   # 标量取首行
  }
}

## ---- 调 prisma_flow 出图(counts 算术不一致仅 message 警告,不停)----
cat("Step 2/3: 绘制 PRISMA 2020 流程图...\n")
to_png <- function(pdf) { png <- sub("\\.pdf$", ".png", pdf)
  suppressWarnings(pdftools::pdf_convert(pdf, format = "png", dpi = 150, pages = 1, filenames = png, verbose = FALSE)); invisible(png) }
f_pdf <- file.path(outdir, "prisma.pdf")
prisma_flow(counts, f_pdf, cex = cex)
to_png(f_pdf)

## ---- 回写解析后的计数汇总(便于核对)----
cat("Step 3/3: 写出计数汇总表...\n")
summ <- data.frame(
  field = names(counts),
  detail = vapply(counts, function(v) {
    if (!is.null(names(v))) paste(sprintf("%s=%d", names(v), v), collapse = "; ")
    else as.character(v)
  }, character(1)),
  total = vapply(counts, function(v) sum(as.integer(v)), integer(1)),
  row.names = NULL, stringsAsFactors = FALSE
)
write.csv(summ, file.path(outdir, "prisma_counts.csv"), row.names = FALSE)

cat(sprintf("完成。PRISMA 流程图 + 计数汇总写入 %s\n", outdir))
