# BaituF8 脱敏说明

## 1. 原始数据不公开原因

原始 BaituF8 feeder 数据包含潜在可识别的工程资产信息（含设备/实体语义与部署关联线索）。
按照公开策略与审计结论，本公开仓库不发布该类敏感原始数据。

## 2. 脱敏后保留的可复现实验特征

为保证论文实验可复核性，脱敏后保留以下关键特征：

- 维度信息（节点数、线路数、设备数量级）
- 决策变量类型（连续、二值阈值化）
- 决策变量边界范围
- 权重参数（alpha/beta/gamma）
- 约束区间（电压上下限）
- 固定 seeds
- 汇总级性能与统计结果
- PF-call budget fairness 验证摘要

## 3. 去除内容

- 可识别的工程单位/实体名称
- 原始 feeder 标识与可追溯场站语义
- 运行级敏感明细（尤其可反推工程侧结构的记录）

## 4. 哪些结果表来自实际工程数据汇总

以下表格包含 BaituF8 实际工程数据链路的“汇总级”公开结果（脱敏后）：

- `results/Table_C_Performance_Summary.csv`（BaituF8-redacted 行）
- `results/Table_D_Statistical_Tests.csv`（BaituF8-redacted 对比行）
- `results/fairness_check/pf_budget_summary.csv`（BaituF8-redacted 行）
- `results/fairness_check/pf_budget_failure_breakdown.csv`（BaituF8-redacted 行）

