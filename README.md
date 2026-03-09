# Minimal Public Reproduction Repository (`paper-repro`)

## 1) 项目标题

面向论文复现的最小公开仓库（Minimal Public Reproduction Repository）。

## 2) 与论文标题对应说明

本仓库对应论文：`<FINAL_PAPER_TITLE_TO_BE_CONFIRMED>`（最终标题待作者在发布前回填）。

本仓库仅包含“可公开、可审计、可最小复现”的实验资产，聚焦论文中的关键结果复核与流程透明化。

## 3) 项目简介（用于复现实验）

- 提供 IEEE33 / IEEE69 的公开可复现配置、种子与结果表。
- 提供 BaituF8 的脱敏配置摘要与汇总结果（不含原始敏感 feeder 数据）。
- 提供关键论文表格 `Table A/B/C/D` 与 PF-call budget fairness validation 公开摘要。
- 提供最小可执行 CLI 接口，用于：
  - 查看配置
  - 查看固定种子
  - 按系统筛选结果摘要
  - 校验 PF-call budget fairness
  - 重建/导出关键表（不重跑实验）

## 4) 环境要求（Python 版本 + 主要依赖）

- Python: `>=3.10`（建议 `3.11+`）
- 主要依赖见 `requirements.txt`：
  - `PyYAML`
  - `numpy`
  - `scipy`

## 5) 安装步骤

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## 6) 运行方式（IEEE33 / IEEE69 / BaituF8 脱敏）

> 说明：该公开仓库默认使用随仓结果进行复核，不触发大规模实验重跑。

```bash
# IEEE33
python src/main_experiment.py --system IEEE33 --action summarize

# IEEE69
python src/main_experiment.py --system IEEE69 --action summarize

# BaituF8 脱敏
python src/main_experiment.py --system BaituF8-redacted --action summarize
```

也可查看配置和种子：

```bash
python src/main_experiment.py --system IEEE33 --action show-config
python src/main_experiment.py --system IEEE33 --action show-seeds
```

## 7) 如何生成关键表（Table A/B/C/D）

关键表已随仓提供在 `results/`。如需按公开资产重新导出（不重跑实验）：

```bash
python src/main_experiment.py --action rebuild-tables --output results
```

输出文件：

- `results/Table_A_System_and_Config.csv`
- `results/Table_B_Algorithm_Settings.csv`
- `results/Table_C_Performance_Summary.csv`
- `results/Table_D_Statistical_Tests.csv`

## 8) 数据说明（IEEE 公开、BaituF8 仅脱敏）

- IEEE33 / IEEE69：提供公开复现所需配置摘要、固定种子与结果表。
- BaituF8：仅公开脱敏后的配置摘要、变量维度/类型/边界与汇总结果。
- 不公开内容：原始工程 feeder 拓扑明细、可识别设备/实体信息、运行级敏感原始记录。

## 9) 复现声明

- 固定 seed：见 `seeds/*.csv`
- run-level logging：由原实验链路导出的 run-level 证据已做公开分级处理
- PF-call budget fairness validation：见 `results/fairness_check/`
- 本公开仓库不修改原项目算法逻辑、评估流程、随机控制与缓存行为；不重跑大规模实验

### 关于 MOEA/D 与 NSGA-III 接口说明

- `src/moead.py` 与 `src/nsga3.py` 提供公开复现实验接口/占位实现路径（可执行、可审计）。
- 当前版本的公开复核以结果表复核为主（`results/Table_C_Performance_Summary.csv`、`results/Table_D_Statistical_Tests.csv`）。
- 不在本仓库中伪造新结果。

## 10) 引用方式（论文 + Zenodo DOI 占位）

### 论文引用（占位）

```text
<Authors>. <FINAL_PAPER_TITLE_TO_BE_CONFIRMED>. <Journal>, <Year>.
```

### 仓库/数据归档引用（Zenodo DOI 占位）

```text
<Authors> (2026). Minimal Public Reproduction Repository (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

发布后请将 DOI 正式号回填到：

- `README.md`
- `CITATION.cff`
- 论文 Data Availability Statement（见 `docs/github_zenodo_release.md`）
