# GitHub + Zenodo 发布步骤

## 1) 本地初始化 git 命令

```bash
git init
git branch -M main
git add .
git commit -m "chore: initialize minimal public reproduction repository"
```

## 2) 提交到 GitHub 命令

```bash
git remote add origin https://github.com/<ORG_OR_USER>/<REPO_NAME>.git
git push -u origin main
```

## 3) Release 命名建议

- 首次公开建议：`v1.0.0`
- 后续修订：`v1.0.1`, `v1.1.0`（遵循语义化版本）

示例：

```bash
git tag v1.0.0
git push origin v1.0.0
```

## 4) Zenodo 绑定并生成 DOI 步骤

1. 登录 Zenodo（或 sandbox 先演练）。
2. 在 Zenodo 中连接 GitHub 账户。
3. 在 Zenodo 的 GitHub 列表中启用本仓库。
4. 在 GitHub 创建 Release（如 `v1.0.0`）。
5. Zenodo 自动抓取 release 并生成 DOI。
6. 记录 concept DOI 与 version DOI。

## 5) DOI 回填位置与示例文本

### A. 回填位置

- `README.md` 的“引用方式”部分
- `CITATION.cff` 的 `doi` 字段
- 论文 Data Availability Statement

### B. 示例文本

#### README / CITATION.cff

```text
Zenodo DOI: https://doi.org/10.5281/zenodo.1234567
```

#### 论文 Data Availability Statement（示例）

```text
The minimal public reproduction package associated with this study is openly available at Zenodo: https://doi.org/10.5281/zenodo.1234567. The repository includes IEEE33/IEEE69 reproducible assets and redacted BaituF8 summary-level materials. Raw engineering feeder data are not publicly released due to confidentiality constraints.
```

