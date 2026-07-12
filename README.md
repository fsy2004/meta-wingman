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

## 快速开始(三步,无需装 Node)

**前置**:Windows,已装 [R 4.x](https://mirrors.tuna.tsinghua.edu.cn/CRAN/) 与 [Python 3.9+](https://www.python.org/downloads/)。

1. **下载** [`install.bat`](https://gitee.com/fsy2004/meta-wingman/raw/master/install.bat)(只需这一个文件)。
2. **双击运行 `install.bat`** —— 它会自动从 Gitee 把整个应用拉下来,并装好 R / Python 依赖(清华镜像)。
3. **双击 `start.bat`** —— 启动后自动打开浏览器 `http://localhost:8000`。

> 界面顶部有**环境状态条**:缺依赖时点「一键安装缺失依赖」即可自动补齐。
> 前端已预构建(`frontend/dist`),终端用户**无需安装 Node.js**;后端在同端口一并托管界面。

<details><summary>开发者:从源码手动跑</summary>

```powershell
powershell -ExecutionPolicy Bypass -File setup\install.ps1   # 装依赖
python setup\env_check.py                                    # 体检(可选)
cd backend ; python -m uvicorn app:app --app-dir . --port 8000   # 后端(同端口托管 dist)→ http://localhost:8000
# 改前端需重建:cd frontend ; npm install ; npm run build
```
</details>

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
