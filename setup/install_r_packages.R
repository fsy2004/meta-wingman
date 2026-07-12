## Meta Wingman: 安装缺失的 R 包(清华 CRAN 镜像;Windows 默认装二进制,免编译)
options(repos = c(CRAN = "https://mirrors.tuna.tsinghua.edu.cn/CRAN"))
need <- c("metafor", "meta", "netmeta", "mada", "bayesmeta", "robvis",
          "metasens", "estmeansd", "pdftools", "gridExtra", "ggplot2")
ip <- rownames(installed.packages())
missing <- need[!need %in% ip]
if (length(missing) == 0) {
  cat("所有 R 包已就绪,无需安装。\n")
} else {
  cat("需安装:", paste(missing, collapse = ", "), "\n")
  install.packages(missing)                       # Windows: type='binary' 默认,免编译
  still <- missing[!missing %in% rownames(installed.packages())]
  if (length(still)) cat("⚠️ 仍未装上(请检查网络或手动装):", paste(still, collapse = ", "), "\n")
  else cat("✅ R 包安装完成。\n")
}
