#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最小 cache 一致性验证：固定 IEEE69 + DE，cache on/off 各跑 2 次。"""

from __future__ import annotations

import argparse
import csv
import json
import shlex
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extended_experiment import build_bounds, build_system_library, load_config_file
from run_pf_budget_experiment import (
    _load_de_budgets,
    _load_seed_map,
    _run_single_with_budget,
    _select_seeds,
)


def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _append_run_command(log_path: Path, argv: List[str]) -> None:
    _ensure_dir(log_path.parent)
    quoted = " ".join(shlex.quote(x) for x in argv)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{_iso_now()} python {quoted}\n")


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    _ensure_dir(path.parent)
    if not rows:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["empty"])
        return

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _format_float(x: float, nd: int = 12) -> str:
    return f"{x:.{nd}f}"


def _write_report(
    report_path: Path,
    *,
    system: str,
    algorithm: str,
    seeds: List[int],
    budget: int,
    threshold: float,
    diffs: List[Dict[str, Any]],
    pass_check: bool,
    max_abs_diff: float,
    cache_runs_csv: Path,
) -> None:
    _ensure_dir(report_path.parent)

    lines: List[str] = []
    lines.append("# Cache Validation Report (Minimal Check)")
    lines.append("")
    lines.append(f"- Generated at: {_iso_now()}")
    lines.append(f"- Scope: {system} + {algorithm}")
    lines.append("- Design: cache off 2 runs + cache on 2 runs (same seeds)")
    lines.append(f"- Total runs: 4")
    lines.append(f"- Seeds: {seeds}")
    lines.append(f"- Budget: {budget}")
    lines.append(f"- Threshold: abs diff < {threshold}")
    lines.append(f"- Data file: `{cache_runs_csv.as_posix()}`")
    lines.append("")

    lines.append("## Per-seed comparison")
    lines.append("")
    lines.append("| seed | final_fitness (off) | final_fitness (on) | abs diff | pass |")
    lines.append("|---:|---:|---:|---:|:---:|")
    for d in diffs:
        ok = d["abs_diff_final_fitness"] < threshold
        lines.append(
            "| "
            + f"{d['seed']} | {_format_float(d['final_fitness_off'])} | {_format_float(d['final_fitness_on'])}"
            + f" | {_format_float(d['abs_diff_final_fitness'])} | {'✅' if ok else '❌'} |"
        )
    lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    lines.append(f"- max abs diff (final_fitness): {_format_float(max_abs_diff)}")
    lines.append(f"- pass (< {threshold}): {pass_check}")

    if pass_check:
        lines.append("- Result: cache on/off consistency passed for minimal verification.")
    else:
        lines.append("- Result: threshold violation detected. Possible reasons include floating-point accumulation order, hidden stochastic paths, or environment-level numerical differences.")
        lines.append("- Note: values are reported transparently without suppression.")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run minimal cache consistency validation")
    parser.add_argument("--config", default="configs/paper.yaml", help="配置文件路径")
    parser.add_argument("--summary_csv", default="needs0301/data/summary.csv", help="预算来源 summary.csv")
    parser.add_argument("--seed_list_path", default="needs0301/data/seed_list.json", help="seed 列表来源")
    parser.add_argument("--system", default="IEEE69", help="验证系统（默认 IEEE69）")
    parser.add_argument("--algorithm", default="DE", choices=["DE"], help="验证算法（固定 DE）")
    parser.add_argument("--runs_per_system", type=int, default=2, help="每 cache 模式运行次数")
    parser.add_argument("--threshold", type=float, default=1e-4, help="一致性阈值")
    parser.add_argument("--out_root", default="needs0305", help="输出目录")
    return parser


def main(argv: List[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    out_root = Path(args.out_root)
    data_dir = out_root / "data"
    logs_dir = out_root / "logs"
    _ensure_dir(data_dir)
    _ensure_dir(logs_dir)

    _append_run_command(logs_dir / "run_command.txt", (argv if argv is not None else sys.argv[1:]))

    if int(args.runs_per_system) != 2:
        raise ValueError("最小验证固定要求 --runs_per_system=2")

    system = str(args.system)
    algorithm = str(args.algorithm)
    threshold = float(args.threshold)

    budgets = _load_de_budgets(Path(args.summary_csv), [system])
    budget = int(budgets[system])

    seed_map = _load_seed_map(Path(args.seed_list_path))
    selected_seeds_map = _select_seeds(seed_map, [system], int(args.runs_per_system))
    seeds = [int(x) for x in selected_seeds_map[system]]

    cfg = load_config_file(Path(args.config))
    system_library = build_system_library()
    if system not in system_library:
        raise ValueError(f"未知系统: {system}")
    system_spec = system_library[system]
    bounds = build_bounds(system_spec)

    rows: List[Dict[str, Any]] = []
    for cache_enabled, cache_tag in ((False, "off"), (True, "on")):
        for run_idx, seed in enumerate(seeds, start=1):
            rec = _run_single_with_budget(
                system_id=system,
                algorithm=algorithm,
                run_idx=run_idx,
                seed=int(seed),
                budget=budget,
                cache_enabled=cache_enabled,
                max_pf_calls_mode="iter_cap_retry",
                base_cfg=cfg,
                bounds=bounds,
                system_spec=system_spec,
            )
            rows.append(
                {
                    "cache": cache_tag,
                    "system": rec["system"],
                    "algorithm": rec["algorithm"],
                    "seed": int(rec["seed"]),
                    "run_id": rec["run_id"],
                    "final_fitness": float(rec["final_fitness"]),
                    "loss_kW": float(rec["loss_kW"]),
                    "voltage_dev_pu": float(rec["voltage_dev_pu"]),
                    "cost_abs_usd_per_year": float(rec["cost_abs_usd_per_year"]),
                    "pf_calls": int(rec["pf_calls"]),
                    "max_pf_calls": int(rec["max_pf_calls"]),
                    "iterations_used": int(rec["iterations_used"]),
                    "retry_count": int(rec["retry_count"]),
                    "runtime_sec": float(rec["runtime_sec"]),
                    "timestamp": rec["timestamp"],
                }
            )

    cache_runs_csv = data_dir / "cache_check_runs.csv"
    _write_csv(cache_runs_csv, rows)

    off_map = {int(r["seed"]): r for r in rows if r["cache"] == "off"}
    on_map = {int(r["seed"]): r for r in rows if r["cache"] == "on"}

    diffs: List[Dict[str, Any]] = []
    for seed in seeds:
        a = off_map[seed]
        b = on_map[seed]
        diffs.append(
            {
                "seed": int(seed),
                "final_fitness_off": float(a["final_fitness"]),
                "final_fitness_on": float(b["final_fitness"]),
                "abs_diff_final_fitness": abs(float(a["final_fitness"]) - float(b["final_fitness"])),
                "pf_calls_off": int(a["pf_calls"]),
                "pf_calls_on": int(b["pf_calls"]),
                "abs_diff_pf_calls": abs(int(a["pf_calls"]) - int(b["pf_calls"])),
            }
        )

    max_abs_diff = max((float(x["abs_diff_final_fitness"]) for x in diffs), default=0.0)
    pass_check = bool(max_abs_diff < threshold)

    report_path = logs_dir / "cache_validation_report.md"
    _write_report(
        report_path,
        system=system,
        algorithm=algorithm,
        seeds=seeds,
        budget=budget,
        threshold=threshold,
        diffs=diffs,
        pass_check=pass_check,
        max_abs_diff=max_abs_diff,
        cache_runs_csv=cache_runs_csv,
    )

    print(
        json.dumps(
            {
                "timestamp": _iso_now(),
                "system": system,
                "algorithm": algorithm,
                "seeds": seeds,
                "budget": budget,
                "runs_total": len(rows),
                "runs_off": len([r for r in rows if r["cache"] == "off"]),
                "runs_on": len([r for r in rows if r["cache"] == "on"]),
                "threshold": threshold,
                "max_abs_diff_final_fitness": max_abs_diff,
                "pass": pass_check,
                "cache_runs_csv": str(cache_runs_csv),
                "report": str(report_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main(sys.argv[1:])
