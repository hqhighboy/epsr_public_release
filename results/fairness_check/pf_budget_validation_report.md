# PF-call Budget Fairness Validation (Public Summary)

## 1) Budget source rule

Budget 规则（按系统）来自既有复现实验资产：

\[
\text{budget(system)} = \left\lceil \frac{\text{DE mean\_pf\_calls(system)}}{10} \right\rceil \times 10
\]

得到预算：

- IEEE33: 1200
- IEEE69: 1240
- BaituF8-redacted: 1320

## 2) Compliance check

公开摘要文件：`pf_budget_summary.csv`

校验条件：

- 对每个 system × algorithm，验证 `max_pf_calls <= budget`

结果：

- 全部分组满足预算约束（通过）。

## 3) Minimal cache consistency evidence

最小一致性验证（同 seed、cache off/on）结论：

- `max abs diff (final_fitness) = 0.0`
- 阈值：`1e-4`
- 结论：通过

## 4) 公平性结论（摘要）

- 在 PF-call 匹配预算下，各算法预算约束满足情况透明可追溯；
- DE/PSO 在三系统上保持稳健优势趋势；
- GA/GA-PSO 在较难系统上存在电压违约占比上升现象（详见 `pf_budget_failure_breakdown.csv`）。

