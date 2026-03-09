#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基于 run-level 数据进行统计检验并生成论文统计对比文件。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.stats import mannwhitneyu, wilcoxon


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    gt = 0
    lt = 0
    for xi in x:
        gt += int(np.sum(xi > y))
        lt += int(np.sum(xi < y))
    denom = len(x) * len(y)
    return float((gt - lt) / denom) if denom else 0.0


def bootstrap_ci_diff_median(x: np.ndarray, y: np.ndarray, n_boot: int = 1000, alpha: float = 0.05) -> Tuple[float, float]:
    if len(x) == 0 or len(y) == 0:
        return 0.0, 0.0
    rng = np.random.default_rng(20260301)
    diffs = np.zeros(n_boot)
    for i in range(n_boot):
        xb = rng.choice(x, size=len(x), replace=True)
        yb = rng.choice(y, size=len(y), replace=True)
        diffs[i] = np.median(xb) - np.median(yb)
    lo = float(np.quantile(diffs, alpha / 2))
    hi = float(np.quantile(diffs, 1 - alpha / 2))
    return lo, hi


def load_runs(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def grouped_metric(rows: List[Dict[str, Any]], system: str, algorithm: str, metric: str) -> np.ndarray:
    vals = [float(r[metric]) for r in rows if r["system"] == system and r["algorithm"] == algorithm]
    return np.array(vals, dtype=float)


def _wilcoxon_if_applicable(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) != len(y) or len(x) == 0:
        return None
    try:
        stat, p = wilcoxon(x, y, zero_method="wilcox", correction=False, alternative="two-sided")
        _ = stat
        return float(p)
    except Exception:
        return None


def run_stat_tests(runs_jsonl: Path, out_csv: Path, report_md: Path) -> None:
    rows = load_runs(runs_jsonl)
    systems = sorted({r["system"] for r in rows})
    algorithms = sorted({r["algorithm"] for r in rows})
    baseline = "GA-PSO" if "GA-PSO" in algorithms else algorithms[0]

    result_rows: List[Dict[str, Any]] = []
    report_lines = ["# stat_tests_report", ""]

    for sys in systems:
        report_lines.append(f"## System: {sys}")
        for algo in algorithms:
            if algo == baseline:
                continue

            x = grouped_metric(rows, sys, baseline, "fitness")
            y = grouped_metric(rows, sys, algo, "fitness")
            if len(x) == 0 or len(y) == 0:
                continue

            u_stat, p_value = mannwhitneyu(x, y, alternative="two-sided")
            p_wilcoxon = _wilcoxon_if_applicable(x, y)
            delta = cliffs_delta(x, y)
            ci_lo, ci_hi = bootstrap_ci_diff_median(x, y)

            row = {
                "system": sys,
                "baseline_algorithm": baseline,
                "compared_algorithm": algo,
                "test": "Mann-Whitney U",
                "metric": "fitness",
                "u_statistic": float(u_stat),
                "p_value": float(p_value),
                "wilcoxon_p_value": float(p_wilcoxon) if p_wilcoxon is not None else "",
                "effect_size_cliffs_delta": float(delta),
                "bootstrap_95ci_median_diff_low": float(ci_lo),
                "bootstrap_95ci_median_diff_high": float(ci_hi),
            }
            result_rows.append(row)

            wtxt = f", wilcoxon_p={p_wilcoxon:.6g}" if p_wilcoxon is not None else ""
            report_lines.append(f"- {baseline} vs {algo}: p={p_value:.6g}{wtxt}, cliff={delta:.4f}, CI=[{ci_lo:.6g}, {ci_hi:.6g}]")
        report_lines.append("")

    if result_rows:
        keys = list(result_rows[0].keys())
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(result_rows)
    else:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["empty"])

    report_md.write_text("\n".join(report_lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="统计检验")
    parser.add_argument("--runs", required=True, help="runs.jsonl 路径")
    parser.add_argument("--out_csv", required=True, help="输出CSV路径")
    parser.add_argument("--report", required=True, help="输出报告md路径")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_stat_tests(Path(args.runs), Path(args.out_csv), Path(args.report))


if __name__ == "__main__":
    main()
