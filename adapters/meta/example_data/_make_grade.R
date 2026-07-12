## 生成 GRADE / SoF 示例数据。GRADE 是纯逻辑模块(无上游内置数据集),
## 故手工构造一张典型 Summary-of-Findings 输入表:每行一个结局,
## 列 = label, design(rct/observational), 五个降级域(rob/inconsistency/
## indirectness/imprecision/pubbias, 取 0/-1/-2), 三个升级域(large_effect/
## dose_response/plausible_confounding, 取 0/1/2)。数值为审稿人判读结果示例。
out <- data.frame(
  label                  = c("All-cause mortality", "Serious adverse events",
                             "Symptom improvement", "Hospital readmission",
                             "Quality of life"),
  design                 = c("rct", "rct", "rct", "observational", "observational"),
  rob                    = c(0,   -1,   0,   -1,   0),
  inconsistency          = c(0,    0,  -1,    0,  -1),
  indirectness           = c(0,    0,   0,   -1,   0),
  imprecision            = c(-1,  -1,   0,    0,  -1),
  pubbias                = c(0,    0,  -1,    0,   0),
  large_effect           = c(0,    0,   0,    2,   0),
  dose_response          = c(0,    0,   0,    0,   1),
  plausible_confounding  = c(0,    0,   0,    0,   0),
  stringsAsFactors = FALSE
)
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(out, file.path(dir, "grade.csv"), row.names = FALSE)
cat("wrote", nrow(out), "rows ->", file.path(dir, "grade.csv"), "\n")
