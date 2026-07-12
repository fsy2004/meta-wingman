# 🪽 Meta Wingman · Meta 分析一站式

> 你的 Meta 分析副驾 —— **准备数据 → 选方法 → 出图出表**,全程本地运行,数据不出本机。

**这是什么:** 一款**本地优先的元分析 / 系统评价桌面软件**(local-first meta-analysis & systematic-review desktop app)。它把 R 的元分析生态(`metafor` / `meta` / `netmeta` / `mada` / `bayesmeta` / `robvis` …)封装成**点选式图形界面**:选方法、填参数、一键得到**发表级图表**。

**定位对标:** 类似 RevMan / CMA / JASP / MetaInsight,差异化在三点 —— **① 本地**(数据不出机,不是托管网页)· **② 覆盖系统评价全流程**(不止效应量合并,含 PRISMA 流程图、RoB 偏倚风险、GRADE 证据分级)· **③ 大陆友好**(依赖走清华镜像、应用从 Gitee / GitHub 一键下载)。不是「又一个统计软件」,而是把顶刊 Meta 常用方法收拢到一个界面、并跟随顶刊持续更新方法的**工作台**。

## 下载地址(两个仓库内容同步)

| 仓库 | 地址 | 适合 |
|------|------|------|
| **Gitee**(默认·国内快) | https://gitee.com/fsy2004/meta-wingman | 中国大陆用户 |
| **GitHub** | https://github.com/fsy2004/meta-wingman | 海外 / 想 star 的用户 ⭐ |

两个仓库保持同步更新,任选其一即可。

## 覆盖的方法(11 种)

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
| 数据准备(中位数→均值±SD) | 从 median/四分位/极差估算 mean±sd(estmeansd) |

所有图统一 **cairo + Arial** 顶刊无衬线标准,矢量出图。

## 快速开始(三步,无需装 Node)

**前置**:Windows,已装 [R 4.x](https://mirrors.tuna.tsinghua.edu.cn/CRAN/) 与 [Python 3.9+](https://www.python.org/downloads/)。版本过低时界面会给出升级方式(见下),**不会自动改动你的系统 R/Python**。

1. **下载** `install.bat`(只需这一个文件):[Gitee](https://gitee.com/fsy2004/meta-wingman/raw/master/install.bat) · [GitHub](https://github.com/fsy2004/meta-wingman/raw/master/install.bat)。
2. **双击运行 `install.bat`** —— 自动拉取整个应用,并装好 R / Python 依赖(默认**清华镜像**)。
3. **启动**:双击 **`start.bat`** —— 它在本机起后端并用系统浏览器打开界面 `http://localhost:8000`。关闭那个最小化的「后端」窗口即停止。

> **环境状态条**(界面顶部)是操作中心:缺依赖 → 选镜像源(默认清华,可切中科大/阿里/官方)后点「一键安装缺失依赖」;R/Python 版本过低 → 给出 `winget` 命令与镜像下载链接,由你手动升级。
> 前端已预构建(`frontend/dist`),终端用户**无需安装 Node.js**;后端在同端口一并托管界面。

### 镜像与默认设置

| 项 | 默认 | 可选 |
|----|------|------|
| 应用下载源 | **Gitee** | GitHub |
| pip / CRAN 源 | **清华 TUNA** | 中科大 / 阿里云 / 官方源 |
| 版本门槛 | Python ≥ 3.9,R ≥ 4.0 | 见 `config/requirements.json` |

镜像源注册表在 `config/sources.json`,版本门槛与依赖清单在 `config/requirements.json`(改一处即全局生效)。

<details><summary>开发者:从源码手动跑</summary>

```powershell
# 装依赖(默认清华;可传源:-PipIndex/-PipTrustedHost/-CranRepo)
powershell -ExecutionPolicy Bypass -File setup\install.ps1
python setup\env_check.py                                    # 体检(可选)
cd backend ; python -m uvicorn app:app --app-dir . --port 8000   # 后端(同端口托管 dist)→ http://localhost:8000
# 改前端需重建:cd frontend ; npm install ; npm run build
```
</details>

## 输入数据

每个方法选中后,界面会说明所需的 CSV 列(例如配对二分类需 `ai,bi,ci,di` + 研究名列)。`adapters/meta/example_data/` 下每个方法都自带一份可直接跑的示例数据(界面上可一键下载作模板)。

> 当前版本以内置示例数据演示完整流程;**载入你自己的 CSV(上传 / 选文件)将在下一版接入**(后端 `inputs`/`path` 通道已就绪,待前端接线)。

## 目录结构

```
meta-wingman/
├─ backend/       FastAPI:环境体检 + 内存红绿灯 + 子进程执行(app/doctor/runner)
├─ frontend/      React + RJSF 界面(App/EnvBar/CsvTable/lib;参数表单由 JSON Schema 自动生成)
├─ adapters/meta/ 各方法的 CLI 适配脚本(共用 _common.R)+ 示例数据
├─ manifests/     每个方法一份 JSON(参数 schema + I/O)
├─ config/        sources.json(镜像源)+ requirements.json(版本门槛/依赖)
├─ toolkit/       内置的 Meta 分析工具包(R,MIT)
└─ setup/         环境体检 + 一键安装脚本
```

## 致谢与许可

内置的 `toolkit/` 为 [meta-analysis-toolkit](https://github.com/fsy2004/meta-analysis-toolkit) 的 Meta 分析函数库(MIT),封装 `metafor` / `meta` / `netmeta` / `mada` / `bayesmeta` / `robvis` 等已发表方法。本项目 MIT 许可。
