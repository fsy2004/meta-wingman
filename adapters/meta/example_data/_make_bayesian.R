## 生成贝叶斯 meta 示例数据:经典 BCG 结核疫苗试验(metadat::dat.bcg)的 OR 效应量。
## 用 metafor::escalc 把 2x2 计数转成 log-OR(yi)与标准误(sei=sqrt(vi)),导出 study,yi,sei。
suppressWarnings(suppressMessages(library(metafor)))
data(dat.bcg, package = "metadat")
d  <- dat.bcg
es <- metafor::escalc("OR", ai = d$tpos, bi = d$tneg, ci = d$cpos, di = d$cneg)
out <- data.frame(study = paste(d$author, d$year),
                  yi = as.numeric(es$yi), sei = sqrt(as.numeric(es$vi)))
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(out, file.path(dir, "bayesian.csv"), row.names = FALSE)
cat("wrote", nrow(out), "rows ->", file.path(dir, "bayesian.csv"), "\n")
