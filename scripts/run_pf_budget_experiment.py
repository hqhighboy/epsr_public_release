#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PF-call budget matched fairness check (run-level 导出)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import shlex
import sys
import time
from copy import deepcopy
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extended_experiment import (
    AlgorithmRunner,
    ObjectiveEvaluator,
    build_bounds,
    build_system_library,
    load_config_file,
    success_and_reason,
)
from utils.random import set_global_seed


ALLOWED_ALGORITHMS: Tuple[str, ...] = ("DE", "GA", "PSO", "GA-PSO")
DEFAULT_SYSTEMS: Tuple[str, ...] = ("IEEE33", "IEEE69", "BaituF8")


def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _parse_csv_list(raw: str) -> List[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def _pkg_version(name: str) -> str:
    try:
        return metadata.version(name)
    except Exception:
        return "N/A"


def _append_run_command(log_path: Path, argv: List[str]) -> None:
    _ensure_dir(log_path.parent)
    quoted = " ".join(shlex.quote(x) for x in argv)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{_iso_now()} python {quoted}\n")


def _write_environment_log(path: Path) -> None:
    _ensure_dir(path.parent)
    lines = [
        f"timestamp={_iso_now()}",
        f"python={platform.python_version()}",
        f"implementation={platform.python_implementation()}",
        f"platform={platform.platform()}",
        f"system={platform.system()}",
        f"release={platform.release()}",
        f"machine={platform.machine()}",
        f"processor={platform.processor()}",
        f"numpy={np.__version__}",
        f"PyYAML={_pkg_version('PyYAML')}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _load_de_budgets(summary_csv: Path, systems: List[str]) -> Dict[str, int]:
    rows: Dict[str, float] = {}
    with summary_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("algorithm") == "DE" and row.get("system") in systems:
                rows[row["system"]] = float(row["mean_pf_calls"])

    missing = [s for s in systems if s not in rows]
    if missing:
        raise ValueError(f"summary.csv 缺少系统 DE 的 mean_pf_calls: {missing}")

    return {s: int(math.ceil(rows[s] / 10.0) * 10) for s in systems}


def _load_seed_map(seed_list_path: Path) -> Dict[str, List[int]]:
    raw = json.loads(seed_list_path.read_text(encoding="utf-8"))
    out: Dict[str, List[int]] = {}
    for k, v in raw.items():
        out[k] = [int(x) for x in v]
    return out


def _select_seeds(seed_map: Dict[str, List[int]], systems: List[str], runs_per_system: int) -> Dict[str, List[int]]:
    selected: Dict[str, List[int]] = {}
    for system in systems:
        seeds = seed_map.get(system, [])
        if len(seeds) < runs_per_system:
            raise ValueError(
                f"seed_list.json 中系统 {system} 种子不足: 需要 {runs_per_system}，实际 {len(seeds)}"
            )
        selected[system] = seeds[:runs_per_system]
    return selected


def _evals_per_iteration(algorithm: str) -> int:
    # 当前 extended_experiment 实现中 GA/PSO/DE 每代约 population 次评估；GA-PSO 约 3*population 次评估。
    return 3 if algorithm == "GA-PSO" else 1


def _estimate_iteration_cap(population: int, budget: int, algorithm: str) -> int:
    initial_evals = population
    evals_iter = population * _evals_per_iteration(algorithm)
    if budget <= initial_evals:
        return 0
    return max(0, int((budget - initial_evals) // max(1, evals_iter)))


def _run_single_with_budget(
    *,
    system_id: str,
    algorithm: str,
    run_idx: int,
    seed: int,
    budget: int,
    cache_enabled: bool,
    max_pf_calls_mode: str,
    base_cfg: Any,
    bounds: List[Tuple[float, float]],
    system_spec: Any,
) -> Dict[str, Any]:
    iter_cap = _estimate_iteration_cap(population=int(base_cfg.population), budget=budget, algorithm=algorithm)
    iter_used = iter_cap
    retry_count = 0

    while True:
        cfg = deepcopy(base_cfg)
        cfg.systems = [system_id]
        cfg.algorithms = [algorithm]
        cfg.iterations = int(iter_used)

        set_global_seed(seed)
        evaluator = ObjectiveEvaluator(system=system_spec, config=cfg, cache_enabled=cache_enabled)
        runner = AlgorithmRunner(name=algorithm, bounds=bounds, cfg=cfg, evaluator=evaluator)

        t0 = time.perf_counter()
        result = runner.optimize()
        runtime_sec = float(time.perf_counter() - t0)
        pf_calls = int(evaluator.pf_calls)

        if pf_calls <= budget:
            break

        if max_pf_calls_mode == "iter_cap_retry" and iter_used > 0:
            iter_used = max(0, iter_used - 1)
            retry_count += 1
            continue

        raise RuntimeError(
            f"run 超预算且无法继续收缩迭代: system={system_id}, alg={algorithm}, "
            f"seed={seed}, pf_calls={pf_calls}, budget={budget}, iter_used={iter_used}"
        )

    best_obj = result["best_objective"]
    success, failure_reason = success_and_reason(best_obj, cfg.penalty_eps)

    if pf_calls > budget:
        raise RuntimeError(
            f"run 记录违反预算约束: system={system_id}, alg={algorithm}, seed={seed}, "
            f"pf_calls={pf_calls}, budget={budget}"
        )

    if max_pf_calls_mode == "iter_cap_retry":
        if retry_count > 0:
            budget_mode = "iter_cap_retry:iterations_cap+backoff_retry"
        else:
            budget_mode = "iter_cap_retry:iterations_cap"
    else:
        budget_mode = "iter_cap_only:iterations_cap"

    return {
        "system": system_id,
        "algorithm": algorithm,
        "seed": int(seed),
        "run_id": f"{system_id}_{algorithm}_run{run_idx:03d}",
        "success": bool(success),
        "failure_reason": failure_reason,
        "final_fitness": float(best_obj["fitness"]),
        "loss_kW": float(best_obj["loss_kW"]),
        "voltage_dev_pu": float(best_obj["voltage_dev_pu"]),
        "cost_abs_usd_per_year": float(best_obj["cost_abs_usd_per_year"]),
        "pf_calls": int(pf_calls),
        "runtime_sec": float(runtime_sec),
        "best_feasible_found": bool(best_obj.get("feasible", False)),
        "max_pf_calls": int(budget),
        "budget_enforced_mode": budget_mode,
        "iterations_cap": int(iter_cap),
        "iterations_used": int(iter_used),
        "retry_count": int(retry_count),
        "cache": "on" if cache_enabled else "off",
        "timestamp": _iso_now(),
    }


def _write_jsonl(records: List[Dict[str, Any]], path: Path) -> None:
    _ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_csv(records: List[Dict[str, Any]], path: Path) -> None:
    _ensure_dir(path.parent)
    if not records:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["empty"])
        return

    fields = list(records[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PF-call budget matched fairness check")
    parser.add_argument("--config", default="configs/paper.yaml", help="配置文件路径（沿用主实验口径）")
    parser.add_argument("--systems", default=",".join(DEFAULT_SYSTEMS), help="系统列表，逗号分隔")
    parser.add_argument("--algs", default=",".join(ALLOWED_ALGORITHMS), help="算法列表，逗号分隔")
    parser.add_argument("--runs_per_system", type=int, default=10, help="每系统每算法运行次数")
    parser.add_argument(
        "--seed_list_path",
        default="needs0301/data/seed_list.json",
        help="种子列表文件（必须来自 needs0301）",
    )
    parser.add_argument(
        "--max_pf_calls_mode",
        default="iter_cap_retry",
        choices=["iter_cap_retry", "iter_cap_only"],
        help="预算约束模式",
    )
    parser.add_argument("--cache", default="on", choices=["on", "off"], help="是否启用缓存")
    parser.add_argument("--out", default="needs0305", help="输出目录")
    return parser


def main(argv: List[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    out_root = Path(args.out)
    data_dir = out_root / "data"
    figs_dir = out_root / "figures"
    logs_dir = out_root / "logs"
    scripts_dir = out_root / "scripts"
    for d in (data_dir, figs_dir, logs_dir, scripts_dir):
        _ensure_dir(d)

    _append_run_command(logs_dir / "run_command.txt", (argv if argv is not None else sys.argv[1:]))
    _write_environment_log(logs_dir / "environment.txt")

    systems = _parse_csv_list(args.systems)
    if not systems:
        raise ValueError("--systems 不能为空")

    selected_algs_raw = _parse_csv_list(args.algs)
    if not selected_algs_raw:
        raise ValueError("--algs 不能为空")
    if set(selected_algs_raw) != set(ALLOWED_ALGORITHMS):
        raise ValueError(f"算法集合必须固定为 {set(ALLOWED_ALGORITHMS)}")
    algorithms = [a for a in ALLOWED_ALGORITHMS if a in selected_algs_raw]

    if args.runs_per_system <= 0:
        raise ValueError("--runs_per_system 必须为正整数")

    summary_csv = Path("needs0301/data/summary.csv")
    seed_list_path = Path(args.seed_list_path)
    budgets = _load_de_budgets(summary_csv=summary_csv, systems=systems)
    seed_map = _load_seed_map(seed_list_path)
    selected_seeds = _select_seeds(seed_map=seed_map, systems=systems, runs_per_system=int(args.runs_per_system))

    cfg = load_config_file(Path(args.config))
    cache_enabled = args.cache.lower() == "on"

    system_library = build_system_library()
    invalid_systems = [s for s in systems if s not in system_library]
    if invalid_systems:
        raise ValueError(f"未知系统: {invalid_systems}")

    records: List[Dict[str, Any]] = []
    for system_id in systems:
        system_spec = system_library[system_id]
        bounds = build_bounds(system_spec)
        budget = int(budgets[system_id])
        for algorithm in algorithms:
            for run_idx, seed in enumerate(selected_seeds[system_id], start=1):
                rec = _run_single_with_budget(
                    system_id=system_id,
                    algorithm=algorithm,
                    run_idx=run_idx,
                    seed=int(seed),
                    budget=budget,
                    cache_enabled=cache_enabled,
                    max_pf_calls_mode=args.max_pf_calls_mode,
                    base_cfg=cfg,
                    bounds=bounds,
                    system_spec=system_spec,
                )
                # 强制预算约束：每条 run 都必须满足。
                if int(rec["pf_calls"]) > int(rec["max_pf_calls"]):
                    raise RuntimeError(f"检测到超预算 run: {rec['run_id']}")
                records.append(rec)

    out_jsonl = data_dir / "pf_budget_runs.jsonl"
    out_csv = data_dir / "pf_budget_runs.csv"
    _write_jsonl(records, out_jsonl)
    _write_csv(records, out_csv)

    print(
        json.dumps(
            {
                "timestamp": _iso_now(),
                "total_runs": len(records),
                "systems": systems,
                "algorithms": algorithms,
                "runs_per_system": int(args.runs_per_system),
                "budgets": budgets,
                "cache": "on" if cache_enabled else "off",
                "out_jsonl": str(out_jsonl),
                "out_csv": str(out_csv),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main(sys.argv[1:])
