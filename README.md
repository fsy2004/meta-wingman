# 🪽 Meta Wingman · Meta 分析一站式

> 你的 Meta 分析副驾 —— **准备数据 → 选方法 → 出图出表**,全程本地运行,数据不出本机。

一个本地可交互的 Meta 分析工作台:把常用 Meta 分析方法包在一个界面后面,选方法、填参数、一键得到**发表级图表**。不是托管网页平台,是你在自己电脑上跑的软件。

## 覆盖的方法(10 种)

| 方法 | 输出 |
|------|------|
| 配对 Meta 分析 | 森林图 + 等高线漏斗图 + 发表偏倚(Egger/Begg/trim-fill/PET-PEESE) |
| 单臂比例 Meta | 比例森林图 |
| 异质性分析 | 亚组 + Meta 回归气泡图 |
| 影响分析 / 稳健性 | 留一法 + Baujat + 累积 + GOSH |
| 网络 Meta(NMA) | 网络图 + 排名图 + netsplit + 联赛表 |
| 诊断试验准确性 | SROC 双变量模型 + 敏感度/特异度森林 |
| 贝叶斯随机效应 Meta | 贝叶斯森林 + 后验密度 |
| PRISMA 2020 | 流程图 |
| 偏倚风险(RoB) | 交通灯图 + 汇总图 |
| GRADE | 证据分级 SoF 表 |

所有图统一 **cairo + Arial** 顶刊无衬线标准,矢量出图。

## 快速开始

**前置**:Windows,已装 [R 4.x](https://mirrors.tuna.tsinghua.edu.cn/CRAN/) 与 [Python 3.9+](https://www.python.org/downloads/)。

```powershell
# 1) 一键装依赖(大陆镜像:Python 清华源 + R 包清华 CRAN 免编译)
powershell -ExecutionPolicy Bypass -File setup\install.ps1

# 2) 体检(可选,确认就绪)
python setup\env_check.py

# 3) 启动后端(端口 8000)
cd backend ; python -m uvicorn app:app --port 8000

# 4) 启动前端(另开一个终端,端口 5173)
cd frontend ; npm install ; npm run dev
# 浏览器打开 http://localhost:5173
```

界面顶部有**环境状态条**:缺依赖时点「一键安装缺失依赖」即可自动补齐。

## 输入数据

每个方法选中后,界面会说明所需的 CSV 列(例如配对二分类需 `ai,bi,ci,di` + 研究名列)。`adapters/meta/example_data/` 下每个方法都自带一份可直接跑的示例数据。

## 目录结构

```
meta-wingman/
├─ backend/       FastAPI:环境体检 + 内存红绿灯 + 子进程执行
├─ frontend/      React + RJSF 界面(参数表单由 JSON Schema 自动生成)
├─ adapters/meta/ 各方法的 CLI 适配脚本 + 示例数据
├─ manifests/     每个方法一份 JSON(参数 schema + I/O)
├─ toolkit/       内置的 Meta 分析工具包(R,MIT)
└─ setup/         环境体检 + 一键安装脚本
```

## 致谢与许可

内置的 `toolkit/` 为 [meta-analysis-toolkit](https://gitee.com/) 的 Meta 分析函数库(MIT),封装 `metafor` / `meta` / `netmeta` / `mada` / `bayesmeta` / `robvis` 等已发表方法。本项目 MIT 许可。
