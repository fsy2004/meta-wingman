# Meta Wingman

本地运行的 Meta 分析 / 系统评价工具。选方法、填参数、出图出表,数据不出本机。

底层是 R 的 metafor、meta、netmeta、mada、bayesmeta、robvis 等包,外面套了一层点选式界面,省去自己写脚本。功能上接近 RevMan、CMA、JASP,覆盖效应量合并、异质性、发表偏倚、网络 Meta、诊断试验、PRISMA、RoB、GRADE。

## 下载

两个仓库内容同步,任选其一:

- Gitee(国内较快):https://gitee.com/fsy2004/meta-wingman
- GitHub:https://github.com/fsy2004/meta-wingman

## 安装与启动

需要 Windows,以及 R 4.x 和 Python 3.9 以上。版本过低时界面会提示升级方式,不会自动改动你的 R / Python。

1. 下载 `install.bat` 一个文件（[Gitee](https://gitee.com/fsy2004/meta-wingman/raw/master/install.bat) 或 [GitHub](https://github.com/fsy2004/meta-wingman/raw/master/install.bat)）。
2. 双击 `install.bat`:自动拉取整个应用,并安装 R / Python 依赖(默认用清华镜像)。
3. 双击 `start.bat`:启动后端并打开浏览器 `http://localhost:8000`。关闭该窗口即停止。

前端已预构建,终端用户不需要安装 Node.js。

界面顶部有一条环境状态栏:缺依赖时可以选镜像源(默认清华,也可切中科大 / 阿里 / 官方)后一键安装;R 或 Python 版本过低时会给出 winget 命令和下载链接,由你自己升级。

## 覆盖的方法

| 方法 | 输出 |
|------|------|
| 配对 Meta 分析 | 森林图、等高线漏斗图、发表偏倚(Egger / Begg / trim-fill / PET-PEESE) |
| 单臂比例 Meta | 比例森林图 |
| 异质性分析 | 亚组、Meta 回归气泡图 |
| 影响分析 / 稳健性 | 留一法、Baujat、累积、GOSH |
| 网络 Meta(NMA) | 网络图、排名图、netsplit、联赛表 |
| 诊断试验准确性 | SROC 双变量模型、敏感度 / 特异度森林 |
| 贝叶斯随机效应 Meta | 贝叶斯森林、后验密度 |
| PRISMA 2020 | 流程图 |
| 偏倚风险(RoB) | 交通灯图、汇总图 |
| GRADE | 证据分级 SoF 表 |
| 数据准备 | 从中位数 / 四分位 / 极差估算 mean±sd(estmeansd) |

图统一用 cairo + Arial 输出矢量图。

## 用自己的数据

方法页默认跑内置示例数据。切到「上传我的 CSV」并选择文件,就能换成自己的数据(列名与示例模板一致,界面上可下载模板)。上传的文件只存在本机 `runs/_uploads/`;运行和数据体检的输入路径都限制在上传目录和示例数据内。

## 镜像与默认设置

| 项 | 默认 | 可选 |
|----|------|------|
| 应用下载源 | Gitee | GitHub |
| pip / CRAN 源 | 清华 TUNA | 中科大 / 阿里云 / 官方源 |
| 版本门槛 | Python ≥ 3.9,R ≥ 4.0 | 见 `config/requirements.json` |

镜像源列表在 `config/sources.json`,版本门槛和依赖清单在 `config/requirements.json`,改一处即可。

<details><summary>开发者:从源码运行</summary>

```powershell
# 安装依赖(默认清华;可传 -PipIndex / -PipTrustedHost / -CranRepo 换源)
powershell -ExecutionPolicy Bypass -File setup\install.ps1
python setup\env_check.py                                        # 环境体检(可选)
cd backend ; python -m uvicorn app:app --app-dir . --port 8000   # 后端,同端口托管前端
# 改前端后重建:cd frontend ; npm install ; npm run build
```
</details>

## 目录结构

```
meta-wingman/
├─ backend/       FastAPI:环境体检、内存红绿灯、子进程执行(app / doctor / runner)
├─ frontend/      React + RJSF 界面,参数表单由 JSON Schema 自动生成
├─ adapters/meta/ 各方法的命令行适配脚本(共用 _common.R)与示例数据
├─ manifests/     每个方法一份 JSON(参数 schema 与输入输出)
├─ config/        sources.json(镜像源)、requirements.json(版本门槛与依赖)
├─ toolkit/       内置的 Meta 分析函数库(R,MIT)
└─ setup/         环境体检与安装脚本
```

## 许可

内置的 `toolkit/` 来自 [meta-analysis-toolkit](https://github.com/fsy2004/meta-analysis-toolkit)(MIT),封装 metafor、meta、netmeta、mada、bayesmeta、robvis 等已发表方法。本项目采用 MIT 许可。
