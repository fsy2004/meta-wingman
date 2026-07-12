## 生成 PRISMA 2020 示例计数表(对应 run_all_examples.R 第66-70行的 counts list)。
## 格式:field,subkey,value 三列长表。标量字段 subkey 留空;具名向量字段
## (n_identified 各数据库、n_fulltext_excluded 各排除原因)用多行 + subkey 表示。
rows <- rbind(
  data.frame(field = "n_identified",          subkey = "PubMed",            value = 520),
  data.frame(field = "n_identified",          subkey = "Embase",            value = 610),
  data.frame(field = "n_identified",          subkey = "WoS",               value = 430),
  data.frame(field = "n_duplicates",          subkey = "",                  value = 380),
  data.frame(field = "n_screened",            subkey = "",                  value = 1180),
  data.frame(field = "n_excluded_screen",     subkey = "",                  value = 980),
  data.frame(field = "n_fulltext_sought",     subkey = "",                  value = 200),
  data.frame(field = "n_fulltext_notretrieved", subkey = "",                value = 12),
  data.frame(field = "n_fulltext_assessed",   subkey = "",                  value = 188),
  data.frame(field = "n_fulltext_excluded",   subkey = "Wrong population",  value = 60),
  data.frame(field = "n_fulltext_excluded",   subkey = "No usable data",    value = 48),
  data.frame(field = "n_fulltext_excluded",   subkey = "Duplicate cohort",  value = 15),
  data.frame(field = "n_included_studies",    subkey = "",                  value = 65),
  data.frame(field = "n_included_reports",    subkey = "",                  value = 68)
)
dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
write.csv(rows, file.path(dir, "prisma.csv"), row.names = FALSE)
cat("wrote", nrow(rows), "rows ->", file.path(dir, "prisma.csv"), "\n")
