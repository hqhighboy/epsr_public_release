# BaituF8 Redacted Data Notes

本目录仅包含 BaituF8 工程系统的**脱敏复现资产说明**，不包含原始敏感 feeder 数据。

## 保留内容（用于复现）

- 维度信息（节点/线路/设备数量级）
- 变量类型（连续/二值阈值化）
- 决策变量边界
- 目标函数权重与约束区间
- 固定 seed 列表
- 汇总级结果表（summary-level）

## 去除内容（不可公开）

- 可识别工程单位与实体标识
- 可追溯真实部署场景的 feeder 细节
- 原始运行级敏感工程记录

## 对应文件

- 配置摘要：`../../config/baituf8_redacted.yaml`
- 种子：`../../seeds/baituf8_seeds.csv`
- 结果汇总：`../../results/Table_C_Performance_Summary.csv`
- 公平性摘要：`../../results/fairness_check/`

