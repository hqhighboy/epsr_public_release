# Reproduction Guide

## 1. 目标与边界

本指南用于公开最小复现实验资产的使用与复核，遵循以下边界：

- 不修改原项目算法逻辑、评估流程、随机控制、缓存行为；
- 不重跑原始大规模实验；
- 仅基于已有可公开资产进行复核与结果表重建。

审计结论见：`docs/release_audit.md`。

---

## 2. 目录概览

- `src/`：最小可执行接口（CLI + 参数/评估工具）
- `config/`：IEEE33、IEEE69、BaituF8 脱敏配置
- `data/`：公开数据说明（IEEE）与脱敏说明（BaituF8）
- `seeds/`：固定 seed 列表
- `results/`：关键表 Table A/B/C/D + fairness check 摘要

---

## 3. 环境准备

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

---

## 4. 快速复核命令

### 4.1 查看配置

```bash
python src/main_experiment.py --system IEEE33 --action show-config
python src/main_experiment.py --system IEEE69 --action show-config
python src/main_experiment.py --system BaituF8-redacted --action show-config
```

### 4.2 查看固定 seeds

```bash
python src/main_experiment.py --system IEEE33 --action show-seeds
python src/main_experiment.py --system IEEE69 --action show-seeds
python src/main_experiment.py --system BaituF8-redacted --action show-seeds
```

### 4.3 查看结果摘要

```bash
python src/main_experiment.py --system IEEE33 --action summarize
python src/main_experiment.py --system IEEE69 --action summarize
python src/main_experiment.py --system BaituF8-redacted --action summarize
```

### 4.4 校验 PF-call budget fairness

```bash
python src/main_experiment.py --system IEEE33 --action fairness-check
python src/main_experiment.py --system IEEE69 --action fairness-check
python src/main_experiment.py --system BaituF8-redacted --action fairness-check
```

### 4.5 重建关键表（不重跑实验）

```bash
python src/main_experiment.py --action rebuild-tables --output results
```

---

## 5. Table A/B/C/D 映射

- Table A: `results/Table_A_System_and_Config.csv`
- Table B: `results/Table_B_Algorithm_Settings.csv`
- Table C: `results/Table_C_Performance_Summary.csv`
- Table D: `results/Table_D_Statistical_Tests.csv`

---

## 6. 关于 MOEA/D 与 NSGA-III

- 当前公开仓库中的 `src/moead.py`、`src/nsga3.py` 为复现实验接口/占位实现路径；
- 复核方式是基于公开结果表进行一致性审阅，而非在本仓库伪造/新增实验结果；
- 后续完整实现计划可在版本迭代中补充，但不影响当前公开最小复现目标。

---

## 7. BaituF8 脱敏边界

- 不公开原始 feeder 数据与可识别实体信息；
- 公开脱敏配置摘要、变量边界、seed 以及汇总结果；
- 详情见：`docs/baituf8_redaction.md`。

