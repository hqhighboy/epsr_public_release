# 公开前自检清单（Pre-release Checklist）

- [ ] 1. 仓库范围确认：仅包含 `paper-repro/` 内容，无越界文件。
- [ ] 2. 许可证确认：`LICENSE` 为 MIT，版权主体已回填。
- [ ] 3. 引用元数据确认：`CITATION.cff` 与 `.zenodo.json` 作者/标题/仓库链接已回填。
- [ ] 4. README 完整性确认：独立覆盖环境、安装、运行、表格生成、数据边界、复现声明、引用方式。
- [ ] 5. 敏感信息检查：无绝对路径、无明文密钥/token、无环境指纹日志。
- [ ] 6. BaituF8 脱敏边界确认：不含原始敏感 feeder 数据，仅保留脱敏摘要与汇总表。
- [ ] 7. 结果可追溯确认：Table A/B/C/D 与 fairness_check 摘要文件齐全且与文档一致。
- [ ] 8. seeds/config 自洽确认：`config/*.yaml` 与 `seeds/*.csv` 命名、系统映射一致。
- [ ] 9. CLI 可执行确认：`src/main_experiment.py` 的 `show-config/show-seeds/summarize/fairness-check/rebuild-tables` 可执行。
- [ ] 10. DOI 回填确认：README、CITATION.cff、论文 Data Availability Statement 三处一致。

