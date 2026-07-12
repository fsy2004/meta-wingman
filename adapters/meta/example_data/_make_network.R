## 生成网络 Meta 示例数据:经典糖尿病降糖药网络(netmeta::Senn2013),对比格式。
## 全部列导出:TE, seTE, treat1.long, treat2.long, treat1, treat2, studlab。
data(Senn2013, package = "netmeta")
out <- Senn2013
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(out, file.path(dir, "network.csv"), row.names = FALSE)
cat("wrote", nrow(out), "rows ->", file.path(dir, "network.csv"), "\n")
