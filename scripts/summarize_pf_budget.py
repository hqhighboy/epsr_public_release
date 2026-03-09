#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基于 run-level PF budget 数据自动生成统计汇总与对比图。"""

from __future__ import annotations

import argparse
import csv
import json
import shlex
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


PREFERRED_SYSTEM_ORDER: Tuple[str, ...] = ("IEEE33", "IEEE69", "BaituF8")
PREFERRED_ALGORITHM_ORDER: Tuple[str, ...] = ("DE", "GA", "PSO", "GA-PSO")

METRICS: Tuple[str, ...] = (
    "final_fitness",
    "loss_kW",
    "voltage_dev_pu",
    "cost_abs_usd_per_year",
    "pf_calls",
    "runtime_sec",
)


def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _append_run_command(log_path: Path, argv: Sequence[str]) -> None:
    _ensure_dir(log_path.parent)
    quoted = " ".join(shlex.quote(x) for x in argv)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{_iso_now()} python {quoted}\n")


def _ordered_unique(items: Iterable[str], preferred: Sequence[str] | None = None) -> List[str]:
    seen: set[str] = set()
    unique: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    if not preferred:
        return unique

    ordered_head = [x for x in preferred if x in seen]
    ordered_set = set(ordered_head)
    ordered_tail = [x for x in unique if x not in ordered_set]
    return ordered_head + ordered_tail


def _to_bool(raw: Any) -> bool:
    return str(raw).strip().lower() in {"1", "true", "t", "yes", "y"}


def _safe_float(raw: Any) -> float:
    return float(raw)


def _safe_int(raw: Any) -> int | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if text == "":
        return None
    return int(float(text))


def _load_runs(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"输入文件不存在: {path}")

    required = {
        "system",
        "algorithm",
        "success",
        "failure_reason",
        "final_fitness",
        "loss_kW",
        "voltage_dev_pu",
        "cost_abs_usd_per_year",
        "pf_calls",
        "runtime_sec",
    }

    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("输入 CSV 缺少表头")

        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"输入 CSV 缺少必要字段: {sorted(missing)}")

        has_budget = "max_pf_calls" in reader.fieldnames

        for row in reader:
            rec: Dict[str, Any] = {
                "system": str(row["system"]).strip(),
                "algorithm": str(row["algorithm"]).strip(),
                "success": _to_bool(row["success"]),
                "failure_reason": str(row.get("failure_reason") or "UNKNOWN").strip() or "UNKNOWN",
                "final_fitness": _safe_float(row["final_fitness"]),
                "loss_kW": _safe_float(row["loss_kW"]),
                "voltage_dev_pu": _safe_float(row["voltage_dev_pu"]),
                "cost_abs_usd_per_year": _safe_float(row["cost_abs_usd_per_year"]),
                "pf_calls": _safe_float(row["pf_calls"]),
                "runtime_sec": _safe_float(row["runtime_sec"]),
            }
            if has_budget:
                rec["max_pf_calls"] = _safe_int(row.get("max_pf_calls"))
            rows.append(rec)

    if not rows:
        raise ValueError("输入 CSV 没有数据")
    return rows


def _metric_stats(values: Sequence[float]) -> Dict[str, float]:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return {
            "mean": float("nan"),
            "std": float("nan"),
            "median": float("nan"),
            "min": float("nan"),
            "max": float("nan"),
        }

    std = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
    return {
        "mean": float(arr.mean()),
        "std": std,
        "median": float(np.median(arr)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def _build_tables(
    runs: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[str], List[str]]:
    systems = _ordered_unique([r["system"] for r in runs], preferred=PREFERRED_SYSTEM_ORDER)
    algorithms = _ordered_unique([r["algorithm"] for r in runs], preferred=PREFERRED_ALGORITHM_ORDER)

    grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for rec in runs:
        grouped[(rec["system"], rec["algorithm"])].append(rec)

    has_budget = any(("max_pf_calls" in x and x["max_pf_calls"] is not None) for x in runs)
    budget_by_system: Dict[str, int] = {}
    if has_budget:
        tmp: Dict[str, List[int]] = defaultdict(list)
        for rec in runs:
            b = rec.get("max_pf_calls")
            if b is not None:
                tmp[rec["system"]].append(int(b))
        for system, vals in tmp.items():
            if vals:
                budget_by_system[system] = int(round(float(np.median(np.asarray(vals, dtype=float)))))

    summary_rows: List[Dict[str, Any]] = []
    for system in systems:
        for algorithm in algorithms:
            rows = grouped.get((system, algorithm), [])
            if not rows:
                continue

            n_runs = len(rows)
            success_count = int(sum(1 for x in rows if bool(x["success"])))
            failure_count = int(n_runs - success_count)
            success_rate = float(success_count / n_runs)

            out: Dict[str, Any] = {
                "system": system,
                "algorithm": algorithm,
                "n_runs": n_runs,
                "success_count": success_count,
                "failure_count": failure_count,
                "success_rate": success_rate,
            }
            if system in budget_by_system:
                out["budget"] = int(budget_by_system[system])

            for metric in METRICS:
                stats = _metric_stats([float(r[metric]) for r in rows])
                out[f"mean_{metric}"] = stats["mean"]
                out[f"std_{metric}"] = stats["std"]
                out[f"median_{metric}"] = stats["median"]
                out[f"min_{metric}"] = stats["min"]
                out[f"max_{metric}"] = stats["max"]

            # 别名列，满足“fitness”关键字的直接引用需求。
            out["mean_fitness"] = out["mean_final_fitness"]
            out["std_fitness"] = out["std_final_fitness"]
            out["median_fitness"] = out["median_final_fitness"]
            out["min_fitness"] = out["min_final_fitness"]
            out["max_fitness"] = out["max_final_fitness"]

            summary_rows.append(out)

    compact_rows: List[Dict[str, Any]] = []
    for row in summary_rows:
        compact: Dict[str, Any] = {
            "system": row["system"],
            "algorithm": row["algorithm"],
            "n_runs": row["n_runs"],
            "success_rate": row["success_rate"],
            "mean_final_fitness": row["mean_final_fitness"],
            "std_final_fitness": row["std_final_fitness"],
            "mean_pf_calls": row["mean_pf_calls"],
        }
        if "budget" in row:
            compact["budget"] = row["budget"]
        compact_rows.append(compact)

    # failure_breakdown: system × algorithm × failure_reason（含 count/share）
    # share 分母为对应 system×algorithm 的总 runs。
    all_reasons_raw = _ordered_unique([r["failure_reason"] for r in runs])
    all_reasons = ["NONE"] + sorted([x for x in all_reasons_raw if x != "NONE"])

    failure_rows: List[Dict[str, Any]] = []
    for system in systems:
        for algorithm in algorithms:
            rows = grouped.get((system, algorithm), [])
            if not rows:
                continue

            n_runs = len(rows)
            reason_counts: Dict[str, int] = defaultdict(int)
            for rec in rows:
                reason_counts[rec["failure_reason"]] += 1

            for reason in all_reasons:
                cnt = int(reason_counts.get(reason, 0))
                failure_rows.append(
                    {
                        "system": system,
                        "algorithm": algorithm,
                        "failure_reason": reason,
                        "count": cnt,
                        "share": float(cnt / n_runs),
                    }
                )

    return summary_rows, compact_rows, failure_rows, systems, algorithms


def _write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: Sequence[str] | None = None) -> None:
    _ensure_dir(path.parent)
    if not rows:
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["empty"])
        return

    if fieldnames is None:
        fieldnames = list(rows[0].keys())

    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames))
        w.writeheader()
        w.writerows(rows)


def _write_summary_json(
    path: Path,
    *,
    input_csv: Path,
    runs: List[Dict[str, Any]],
    systems: List[str],
    algorithms: List[str],
    summary_rows: List[Dict[str, Any]],
) -> None:
    _ensure_dir(path.parent)
    payload = {
        "generated_at": _iso_now(),
        "source_csv": str(input_csv),
        "n_total_runs": len(runs),
        "systems": systems,
        "algorithms": algorithms,
        "summary": summary_rows,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _fitness_group_values(
    runs: List[Dict[str, Any]], systems: Sequence[str], algorithms: Sequence[str]
) -> List[Tuple[str, str, List[float]]]:
    grouped: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    for rec in runs:
        grouped[(rec["system"], rec["algorithm"])] += [float(rec["final_fitness"])]

    output: List[Tuple[str, str, List[float]]] = []
    for system in systems:
        for algorithm in algorithms:
            vals = grouped.get((system, algorithm), [])
            if vals:
                output.append((system, algorithm, vals))
    return output


def _plot_fitness_boxplot(
    runs: List[Dict[str, Any]],
    *,
    systems: Sequence[str],
    algorithms: Sequence[str],
    out_png: Path,
    out_pdf: Path,
) -> None:
    grouped = _fitness_group_values(runs, systems=systems, algorithms=algorithms)
    if not grouped:
        raise ValueError("无数据可绘制 fitness 箱线图")

    color_map = {
        "DE": "#4C78A8",
        "GA": "#F58518",
        "PSO": "#54A24B",
        "GA-PSO": "#B279A2",
    }

    n_alg = max(1, len(algorithms))
    group_gap = 1.0

    data: List[List[float]] = []
    positions: List[float] = []
    colors: List[str] = []

    for s_idx, system in enumerate(systems):
        base = s_idx * (n_alg + group_gap)
        for a_idx, algorithm in enumerate(algorithms):
            vals = [x[2] for x in grouped if x[0] == system and x[1] == algorithm]
            if not vals:
                continue
            data.append(vals[0])
            positions.append(base + a_idx)
            colors.append(color_map.get(algorithm, "#888888"))

    fig, ax = plt.subplots(figsize=(10, 5), dpi=180)
    bp = ax.boxplot(
        data,
        positions=positions,
        widths=0.65,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#222222", "linewidth": 1.3},
    )

    for box, color in zip(bp["boxes"], colors):
        box.set_facecolor(color)
        box.set_alpha(0.75)
        box.set_linewidth(1.0)

    for whisker in bp["whiskers"]:
        whisker.set_linewidth(1.0)
    for cap in bp["caps"]:
        cap.set_linewidth(1.0)

    centers = [s_idx * (n_alg + group_gap) + (n_alg - 1) / 2 for s_idx in range(len(systems))]
    ax.set_xticks(centers)
    ax.set_xticklabels(list(systems), fontsize=10)
    ax.set_xlabel("System", fontsize=11)
    ax.set_ylabel("Final fitness", fontsize=11)
    ax.set_title("PF-budget comparison: final fitness distribution", fontsize=12)
    ax.grid(axis="y", alpha=0.3)

    legend_handles = [
        Patch(facecolor=color_map.get(alg, "#888888"), edgecolor="black", alpha=0.75, label=alg)
        for alg in algorithms
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.18),
        ncol=max(1, len(algorithms)),
        frameon=False,
        fontsize=9,
    )

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    _ensure_dir(out_png.parent)
    fig.savefig(out_png, dpi=300)
    fig.savefig(out_pdf)
    plt.close(fig)


def _success_rate_map(summary_rows: List[Dict[str, Any]]) -> Dict[Tuple[str, str], float]:
    out: Dict[Tuple[str, str], float] = {}
    for row in summary_rows:
        out[(str(row["system"]), str(row["algorithm"]))] = float(row["success_rate"])
    return out


def _plot_success_bar(
    summary_rows: List[Dict[str, Any]],
    *,
    systems: Sequence[str],
    algorithms: Sequence[str],
    out_png: Path,
    out_pdf: Path,
) -> None:
    rate_map = _success_rate_map(summary_rows)
    color_map = {
        "DE": "#4C78A8",
        "GA": "#F58518",
        "PSO": "#54A24B",
        "GA-PSO": "#B279A2",
    }

    x = np.arange(len(systems), dtype=float)
    n_alg = max(1, len(algorithms))
    total_width = 0.82
    bar_width = total_width / n_alg

    fig, ax = plt.subplots(figsize=(9, 5), dpi=180)
    for a_idx, algorithm in enumerate(algorithms):
        offset = -total_width / 2 + (a_idx + 0.5) * bar_width
        xpos = x + offset
        rates_pct = [100.0 * rate_map.get((system, algorithm), 0.0) for system in systems]
        bars = ax.bar(
            xpos,
            rates_pct,
            width=bar_width * 0.92,
            color=color_map.get(algorithm, "#888888"),
            edgecolor="black",
            linewidth=0.8,
            label=algorithm,
        )
        for bar, val in zip(bars, rates_pct):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                min(104.0, bar.get_height() + 1.0),
                f"{val:.0f}%",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(list(systems), fontsize=10)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Success rate (%)", fontsize=11)
    ax.set_xlabel("System", fontsize=11)
    ax.set_title("PF-budget comparison: success rate", fontsize=12)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.18),
        ncol=max(1, len(algorithms)),
        frameon=False,
        fontsize=9,
    )

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    _ensure_dir(out_png.parent)
    fig.savefig(out_png, dpi=300)
    fig.savefig(out_pdf)
    plt.close(fig)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize PF-budget runs and generate figures")
    parser.add_argument("--in_csv", default="needs0305/data/pf_budget_runs.csv", help="输入 run-level CSV")
    parser.add_argument("--out_root", default="needs0305", help="输出根目录（仅 needs0305）")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    in_csv = Path(args.in_csv)
    out_root = Path(args.out_root)

    data_dir = out_root / "data"
    fig_dir = out_root / "figures"
    logs_dir = out_root / "logs"

    _ensure_dir(data_dir)
    _ensure_dir(fig_dir)
    _ensure_dir(logs_dir)

    _append_run_command(logs_dir / "run_command.txt", sys.argv)

    runs = _load_runs(in_csv)
    summary_rows, compact_rows, failure_rows, systems, algorithms = _build_tables(runs)

    # IEEE69 failure breakdown 强制检查
    if "IEEE69" in systems:
        ieee69 = [x for x in failure_rows if x["system"] == "IEEE69"]
        if not ieee69:
            raise RuntimeError("failure breakdown 缺少 IEEE69 数据")

    summary_csv = data_dir / "pf_budget_summary.csv"
    summary_json = data_dir / "pf_budget_summary.json"
    compact_csv = data_dir / "pf_budget_table_compact.csv"
    failure_csv = data_dir / "pf_budget_failure_breakdown.csv"

    summary_fields: List[str] = [
        "system",
        "algorithm",
        "n_runs",
        "success_count",
        "failure_count",
        "success_rate",
    ]
    if any("budget" in x for x in summary_rows):
        summary_fields.append("budget")

    for metric in METRICS:
        summary_fields.extend(
            [
                f"mean_{metric}",
                f"std_{metric}",
                f"median_{metric}",
                f"min_{metric}",
                f"max_{metric}",
            ]
        )
    summary_fields.extend(["mean_fitness", "std_fitness", "median_fitness", "min_fitness", "max_fitness"])

    compact_fields: List[str] = [
        "system",
        "algorithm",
        "n_runs",
        "success_rate",
        "mean_final_fitness",
        "std_final_fitness",
        "mean_pf_calls",
    ]
    if any("budget" in x for x in compact_rows):
        compact_fields.append("budget")

    _write_csv(summary_csv, summary_rows, fieldnames=summary_fields)
    _write_summary_json(
        summary_json,
        input_csv=in_csv,
        runs=runs,
        systems=systems,
        algorithms=algorithms,
        summary_rows=summary_rows,
    )
    _write_csv(compact_csv, compact_rows, fieldnames=compact_fields)
    _write_csv(
        failure_csv,
        failure_rows,
        fieldnames=["system", "algorithm", "failure_reason", "count", "share"],
    )

    fig_fitness_png = fig_dir / "Fig_PFbudget_Compare_Fitness.png"
    fig_fitness_pdf = fig_dir / "Fig_PFbudget_Compare_Fitness.pdf"
    fig_success_png = fig_dir / "Fig_PFbudget_Compare_Success.png"
    fig_success_pdf = fig_dir / "Fig_PFbudget_Compare_Success.pdf"

    _plot_fitness_boxplot(
        runs,
        systems=systems,
        algorithms=algorithms,
        out_png=fig_fitness_png,
        out_pdf=fig_fitness_pdf,
    )
    _plot_success_bar(
        summary_rows,
        systems=systems,
        algorithms=algorithms,
        out_png=fig_success_png,
        out_pdf=fig_success_pdf,
    )

    print(
        json.dumps(
            {
                "generated_at": _iso_now(),
                "input_csv": str(in_csv),
                "n_total_runs": len(runs),
                "n_summary_rows": len(summary_rows),
                "n_compact_rows": len(compact_rows),
                "n_failure_rows": len(failure_rows),
                "summary_csv": str(summary_csv),
                "summary_json": str(summary_json),
                "compact_csv": str(compact_csv),
                "failure_csv": str(failure_csv),
                "figures": [
                    str(fig_fitness_png),
                    str(fig_fitness_pdf),
                    str(fig_success_png),
                    str(fig_success_pdf),
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main(sys.argv[1:])

