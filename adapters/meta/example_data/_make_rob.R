## 生成偏倚风险图示例数据:robvis::data_rob2(RoB 2,随机对照试验)。
## 全部列导出:Study, D1..D5, Overall, Weight(D1-D5=五个风险域判断,加权用 Weight)。
data(data_rob2, package = "robvis")
out <- data_rob2
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(out, file.path(dir, "rob.csv"), row.names = FALSE)
cat("wrote", nrow(out), "rows ->", file.path(dir, "rob.csv"), "\n")
