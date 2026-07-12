## 生成诊断准确性(DTA)示例数据:mada::AuditC(AUDIT-C 酒精滥用筛查),2x2 诊断表。
data(AuditC, package = "mada")
d <- AuditC
## AuditC 无研究名列,行名即研究编号 -> 生成 study 列(行号/行名)
study <- if (!is.null(rownames(d)) && any(rownames(d) != as.character(seq_len(nrow(d))))) rownames(d) else paste0("Study ", seq_len(nrow(d)))
out <- data.frame(study = study, TP = d$TP, FN = d$FN, FP = d$FP, TN = d$TN)
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(out, file.path(dir, "diagnostic.csv"), row.names = FALSE)
cat("wrote", nrow(out), "rows ->", file.path(dir, "diagnostic.csv"), "\n")
