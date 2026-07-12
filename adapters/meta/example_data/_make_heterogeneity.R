## 生成异质性(亚组 + Meta 回归)示例数据:BCG 结核疫苗试验(metadat::dat.bcg),
## 二分类 2x2 + 研究级调节变量 ablat(纬度,数值) 与 alloc(分配方式,类别)。
data(dat.bcg, package = "metadat")
d <- dat.bcg
out <- data.frame(study = paste(d$author, d$year),
                  ai = d$tpos, bi = d$tneg, ci = d$cpos, di = d$cneg,
                  ablat = d$ablat, alloc = d$alloc)
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(out, file.path(dir, "heterogeneity.csv"), row.names = FALSE)
cat("wrote", nrow(out), "rows ->", file.path(dir, "heterogeneity.csv"), "\n")
