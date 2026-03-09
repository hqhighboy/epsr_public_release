# 子任务A：公开前内容审计（仅审计与清单输出）

- 审计时间（UTC）：2026-03-06
- 审计范围：当前工作区 `e:/Project/baitu_f8_project`
- 审计目标：服务后续公开仓库重构，形成最小复现资产建议（EPSR 场景）
- 约束声明：本次仅做审计与清单输出；未执行仓库重构/大规模复制/算法逻辑修改/结果改写。

---

## 1. 风险发现摘要

### 1.1 绝对路径风险（已发现）

1) `direct_build.py`
- 发现硬编码本机路径（PyInstaller）
- 示例：`C:\\Users\\hq\\AppData\\Roaming\\Python\\Python313\\Scripts\\pyinstaller.exe`

2) `algorithm_flowchart_graphviz.py`
- 发现硬编码本机 Graphviz 安装路径
- 示例：`C:\\Program Files\\Graphviz\\bin\\dot.exe`

3) `run_test.bat`
- 发现硬编码历史项目绝对目录
- 示例：`d:\\Projects\\article2025\\BaituF8\\baitu_f8_project`

### 1.2 疑似密钥/口令风险（已发现）

1) `config/settings.py`
- 发现硬编码 JWT secret 风格字段：`jwt_secret_key`

2) `docker-compose.yml`
- 发现示例数据库口令：`POSTGRES_PASSWORD: baitu_password`

> 说明：虽可能为开发示例值，但对公开仓库仍应按“凭据样式信息”处理，建议不进入最小复现公开子集。

### 1.3 敏感数据/环境指纹风险（已发现）

1) 机器环境指纹：
- `needs0305/logs/environment.txt`
- `needs0305/cache_check_off/logs/environment.txt`
- `needs0305/cache_check_on/logs/environment.txt`
- `needs0305/cache_check_de_off/logs/environment.txt`

以上文件包含 OS/CPU/Python 版本等环境信息，建议从公开仓库中移除。

2) BaituF8 敏感边界：
- `outputs/paper_v2/data/runs.csv` 与同目录 `runs.jsonl` 包含 `system=BaituF8` 的 run-level 明细（含决策向量、电压曲线等）
- 该类细粒度记录不建议作为公开最小集直接发布，应仅保留脱敏摘要与结果。

---

## 2. 复现主链路识别（EPSR 最小复现）

基于代码与数据链路核查，当前最小可复现主链路为：

1) 配置：`configs/paper.yaml`
2) 实验入口：`scripts/run_experiments.py`
3) 主流程：`extended_experiment.py`
4) 重算一致性：`scripts/recompute_summary.py`
5) 论文工件生成：`scripts/generate_paper_artifacts.py`
6) 统计检验：`scripts/stat_tests.py`
7) 随机种子工具：`utils/random.py`
8) 输出数据（建议分级公开）：`outputs/paper_v2/data/*`

说明：
- `extended_experiment.py` 已覆盖 `IEEE33/IEEE69/BaituF8`。
- 为满足公开策略，应执行“系统级分级”：
  - IEEE33/IEEE69：允许完整复现资产；
  - BaituF8：仅脱敏摘要与结果，不公开敏感原始/细粒度工程数据。

---

## 3. 建议保留清单（按类别）

以下为“公开仓库重构后”的建议保留目标（本子任务仅给清单，不执行重构）：

### 3.1 代码（Code）

**建议保留（核心）**
- `extended_experiment.py`
- `scripts/run_experiments.py`
- `scripts/recompute_summary.py`
- `scripts/generate_paper_artifacts.py`
- `scripts/stat_tests.py`
- `utils/random.py`

**建议保留（可选）**
- `README.md`（需脱敏改写）
- `requirements.txt`（建议修复编码后再公开）

**建议 keep glob**
- `scripts/*.py`
- `utils/*.py`
- `extended_experiment.py`

### 3.2 配置（Config）

**建议保留**
- `configs/paper.yaml`

**建议 keep glob**
- `configs/*.yaml`

### 3.3 数据（Data）

**IEEE33/IEEE69：建议保留完整复现最小数据**
- `outputs/paper_v2/data/runs.csv`
- `outputs/paper_v2/data/runs.jsonl`
- `outputs/paper_v2/data/summary.csv`
- `outputs/paper_v2/data/summary.json`
- `outputs/paper_v2/data/experiment_meta.json`
- `outputs/paper_v2/data/seed_list.json`

**BaituF8：建议仅保留脱敏摘要**
- 可保留：`summary.csv` / `summary.json` 中 BaituF8 聚合指标（脱敏后）
- 不建议公开：BaituF8 的 run-level 行（见排除清单）

**建议 keep glob（经系统分级过滤后）**
- `outputs/paper_v2/data/summary.*`
- `outputs/paper_v2/data/experiment_meta.json`
- `outputs/paper_v2/data/seed_list.json`
- `outputs/paper_v2/data/runs.*`（仅 IEEE33/IEEE69）

### 3.4 种子（Seed）

**建议保留**
- `outputs/paper_v2/data/seed_list.json`

### 3.5 结果（Results）

**建议保留（最小）**
- `outputs/paper_v2/data/summary.csv`
- `outputs/paper_v2/data/summary.json`

**可选保留（如果需论文图复算）**
- 与 `scripts/generate_paper_artifacts.py` 配套的最小图表输入输出

### 3.6 文档（Docs）

**建议保留（需脱敏）**
- 复现说明文档（重写精简版）
- 审计文档：`paper-repro/docs/release_audit.md`

**建议 keep glob**
- `paper-repro/docs/*.md`
- `README.md`（脱敏版）

---

## 4. 建议排除清单（按原因分组）

### 4.1 安全类（Security）

1) 绝对路径/本机依赖硬编码
- `direct_build.py`
- `algorithm_flowchart_graphviz.py`
- `run_test.bat`

原因：暴露本机目录结构与环境细节；不可移植。

2) 凭据/密钥样式配置
- `config/settings.py`（含 `jwt_secret_key`）
- `docker-compose.yml`（含示例数据库口令字段）

原因：公开仓库中应避免出现任何“真实或样式化凭据”字段。

3) 环境指纹日志
- `needs0305/**/logs/environment.txt`
- `needs0305/logs/run_command.txt`

原因：暴露平台、处理器、运行命令细节。

**建议 deny glob（安全）**
- `**/logs/environment.txt`
- `**/logs/run_command.txt`
- `**/*.bat`
- `config/settings.py`
- `docker-compose.yml`

### 4.2 体积类（Size）

1) 大体积中间与可视化产物
- `multi_scenario_comparison.html`
- `network_3d_topology.html`
- 大量 `picture-*` / `Pictures*` / `MyArticle-0227/Figures/*`

2) 重复图件与历史导出
- 根目录及多子目录中大量 `.png/.pdf` 备份版本

原因：显著增大仓库体积，不影响最小可复现。

**建议 deny glob（体积）**
- `picture-*/**`
- `Pictures*/**`
- `MyArticle-0227/Figures/**`
- `**/*.zip`
- `**/*.html`（与复现无直接关联者）

### 4.3 无关性（Irrelevance）

1) 与论文复现主链路无关脚本
- `fix_*.py`
- `test_*.py`
- `debug_*.py`
- `quick_*test*.py`
- `format_paper_for_journal.py`
- 各类临时 patch/文档处理脚本

2) 历史投稿/草稿文档目录
- `needs0301/投稿/**`
- `needs0305/paper/*.docx`
- 根目录多份 `.docx` 草稿与技术文档

原因：非最小复现必需，且混入大量版本历史。

**建议 deny glob（无关）**
- `test_*.py`
- `debug_*.py`
- `fix_*.py`
- `**/*draft*`
- `**/投稿/**`
- `**/*.docx`（除非明确作为公开补充材料）

### 4.4 不可公开（BaituF8 边界）

1) BaituF8 细粒度 run-level 明细
- `outputs/paper_v2/data/runs.csv`
- `outputs/paper_v2/data/runs.jsonl`

原因：包含 `system=BaituF8` 的决策向量/电压曲线等细节，不符合“仅脱敏摘要与结果”原则。

2) 可能关联工程内部语义的数据与文档
- `baitu_f8_bigdata.db`
- `白兔F8*技术文档*.docx`
- `Baitu_F8_Technical_Documentation_*.docx`

原因：可能包含工程资产与不可公开信息。

**建议 deny glob（不可公开）**
- `*baitu*bigdata*.db`
- `*Baitu*Technical*Documentation*.docx`
- `*白兔F8*技术文档*.docx`
- `outputs/paper_v2/data/runs.*`（若未对 BaituF8 分系统拆分过滤）

---

## 5. Keep / Deny 汇总（glob + 示例）

### 5.1 建议 keep（目标态）

```text
scripts/*.py
utils/*.py
extended_experiment.py
configs/*.yaml
outputs/paper_v2/data/summary.*
outputs/paper_v2/data/experiment_meta.json
outputs/paper_v2/data/seed_list.json
outputs/paper_v2/data/runs.*           # 仅 IEEE33/IEEE69
paper-repro/docs/*.md
README.md                              # 脱敏后
```

关键示例文件：
- `scripts/run_experiments.py`
- `extended_experiment.py`
- `configs/paper.yaml`
- `outputs/paper_v2/data/summary.csv`

### 5.2 建议 deny（目标态）

```text
.vscode/**
baitu_env/**
**/__pycache__/**
**/*.pyc
**/*.log
**/*temp*
**/logs/environment.txt
**/logs/run_command.txt
**/*.bat
config/settings.py
docker-compose.yml
picture-*/**
Pictures*/**
MyArticle-0227/Figures/**
**/*.zip
test_*.py
debug_*.py
fix_*.py
**/投稿/**
**/*.docx                               # 默认排除，按公开策略白名单放行
*baitu*bigdata*.db
outputs/paper_v2/data/runs.*            # 若无法先做 BaituF8 过滤拆分
```

关键示例文件：
- `direct_build.py`
- `algorithm_flowchart_graphviz.py`
- `run_test.bat`
- `needs0305/logs/environment.txt`
- `config/settings.py`

---

## 6. 后续重构建议（最小复现子集）

1) 先做“系统级数据拆分”
- 将 run-level 数据按系统拆分为 IEEE33/IEEE69/BaituF8 三份；
- 公开仓库仅保留 IEEE33/IEEE69 的 run-level；
- BaituF8 仅保留 summary 级脱敏结果。

2) 建立发布白名单机制
- 以 keep glob 为主，deny glob 为兜底；
- 构建发布前自动检查（绝对路径、密钥样式、环境指纹、超大文件）。

3) 文档脱敏与许可证澄清
- 重写 `README` 为复现导向说明，删除商业网址/联系方式占位与非学术部署内容；
- 增加明确 `LICENSE` 与第三方依赖声明。

4) 环境可复现改进
- 修复 `requirements.txt` 编码问题（当前疑似 UTF-16/乱码展示）；
- 补充最小运行命令、输入输出契约与校验步骤。

---

## 7. 本次子任务产出与边界确认

- 已完成：目录审计、风险识别、keep/deny 清单、最小复现建议。
- 未执行：仓库重构、文件迁移、算法改写、实验重跑、结果文件内容改写。
- 产出文件：`paper-repro/docs/release_audit.md`
