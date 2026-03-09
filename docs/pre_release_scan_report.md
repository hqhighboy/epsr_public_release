# Pre-release Scan Report

- Scan scope: `paper-repro/`
- Timestamp (UTC): 2026-03-06

## 1) 绝对路径痕迹

扫描规则：`([A-Za-z]:\\|/home/|/Users/|/mnt/)`

发现：

- 命中仅出现在 `docs/release_audit.md` 的审计“证据示例”中：
  - `C:\Users\...`
  - `C:\Program Files\...`
  - `d:\Projects\...`

结论：

- 属于审计报告引用证据，不是可执行配置或代码路径。
- 当前公开仓库运行链路未发现硬编码绝对路径。

## 2) 明文密钥/token 风险模式

扫描规则（大小写不敏感）：

`api_key|secret|token|password|passwd|authorization|bearer|jwt|private_key` 赋值样式

发现：

- 命中仅出现在 `docs/release_audit.md` 的审计描述（`POSTGRES_PASSWORD` 示例文本）。

结论：

- 未在公开代码、配置、脚本中发现可执行层面的凭据赋值。

## 3) 缺失依赖线索

扫描规则：

`ModuleNotFoundError|ImportError|No module named|TODO install`

发现：

- 未发现缺失依赖报错痕迹。
- 文档中出现 `pip install` 命令属于正常安装说明。

结论：

- `requirements.txt` 与当前最小接口依赖一致（PyYAML / numpy / scipy）。

## 4) 文档自洽性（README 是否可独立复现）

检查项：

- 项目标题
- 与论文标题对应说明
- 项目简介
- 环境要求
- 安装步骤
- 运行方式（IEEE33/IEEE69/BaituF8 脱敏）
- 关键表生成方式（Table A/B/C/D）
- 数据说明（IEEE 公开、BaituF8 脱敏）
- 复现声明（seed/run-level/fairness）
- 引用方式（论文 + Zenodo DOI 占位）

结果：

- 以上项目均已覆盖。
- README 可作为独立复现入口文档。

## 5) 风险修复与建议

已完成/确认：

- 已采用脱敏命名 `BaituF8-redacted`（结果与文档侧）。
- 已在 `docs/baituf8_redaction.md` 明确不可公开边界。
- 已提供 MIT 许可证、CITATION、Zenodo 元数据占位。

仍需发布前人工回填：

- 作者姓名与机构
- 论文最终标题
- 仓库地址
- DOI 正式号

