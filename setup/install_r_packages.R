## Meta Wingman: 安装缺失的 R 包 —— 源与包清单由 install.ps1 作为参数传入(取自 config/requirements.json)。
## 用法: Rscript install_r_packages.R <CRAN_repo> <pkg1> <pkg2> ...  (Windows 默认装二进制,免编译)
args <- commandArgs(trailingOnly = TRUE)
repo <- if (length(args) >= 1 && nzchar(args[1])) args[1] else "https://mirrors.tuna.tsinghua.edu.cn/CRAN"
need <- if (length(args) >= 2) args[-1] else
  c("metafor", "meta", "netmeta", "mada", "bayesmeta", "robvis",
    "metasens", "estmeansd", "pdftools", "gridExtra", "ggplot2")
options(repos = c(CRAN = repo))
cat("  R 包安装源:", repo, "\n")

ip <- rownames(installed.packages())
missing <- need[!need %in% ip]
if (length(missing) == 0) {
  cat(sprintf("  所有 R 包已就绪(共 %d 个),无需安装。\n", length(need)))
} else {
  cat(sprintf("  需安装 %d/%d 个:%s\n", length(missing), length(need), paste(missing, collapse = ", ")))
  for (i in seq_along(missing)) {
    p <- missing[i]
    cat(sprintf("  [%d/%d] 安装 %s <- %s ...\n", i, length(missing), p, repo))
    try(install.packages(p), silent = TRUE)
  }
  still <- missing[!missing %in% rownames(installed.packages())]
  if (length(still)) cat("  ⚠️ 仍未装上(检查网络/换源):", paste(still, collapse = ", "), "\n")
  else cat("  ✅ R 包安装完成。\n")
}
