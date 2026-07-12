## 生成配对 meta 示例数据:经典 BCG 结核疫苗试验(metadat::dat.bcg),二分类 2x2。
data(dat.bcg, package = "metadat")
d <- dat.bcg
out <- data.frame(study = paste(d$author, d$year),
                  ai = d$tpos, bi = d$tneg, ci = d$cpos, di = d$cneg)
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(out, file.path(dir, "bcg.csv"), row.names = FALSE)
cat("wrote", nrow(out), "rows ->", file.path(dir, "bcg.csv"), "\n")
