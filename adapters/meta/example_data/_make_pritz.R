## 生成单臂比例 meta 示例数据:Pritz 1997 颅内海绵状血管瘤(metadat::dat.pritz1997)。
## 每行一个研究:xi = 事件数(如手术全切/某结局阳性), ni = 组样本量;单组无对照臂。
data(dat.pritz1997, package = "metadat")
d <- dat.pritz1997
out <- data.frame(study = d$authors, xi = d$xi, ni = d$ni)
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(out, file.path(dir, "proportion.csv"), row.names = FALSE)
cat("wrote", nrow(out), "rows ->", file.path(dir, "proportion.csv"), "\n")
