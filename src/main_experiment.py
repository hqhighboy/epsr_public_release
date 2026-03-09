"""公开最小复现仓库主 CLI。

说明：
1) 默认只做“结果与配置复核”，不重跑完整实验；
2) 提供按系统摘要、种子展示、PF-budget 公平性校验、关键表重建（基于现有公开资产）。
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from constraints import ConstraintInput, check_voltage_limits
from evaluator import summarize_row
from ga import export_config_dict as ga_config
from ga_pso import export_config_dict as gapso_config
from de import export_config_dict as de_config
from moead import export_config_dict as moead_config
from nsga3 import export_config_dict as nsga3_config
from pso import export_config_dict as pso_config
from utils import dump_json, read_csv_rows, read_yaml, resolve_path, write_csv_rows


SYSTEM_ALIAS = {
    "IEEE33": "IEEE33",
    "IEEE69": "IEEE69",
    "BaituF8-redacted": "BaituF8",
}


def _summary_path() -> Path:
    return resolve_path("results/Table_C_Performance_Summary.csv")


def _table_a_path() -> Path:
    return resolve_path("results/Table_A_System_and_Config.csv")


def _table_b_path() -> Path:
    return resolve_path("results/Table_B_Algorithm_Settings.csv")


def _table_d_path() -> Path:
    return resolve_path("results/Table_D_Statistical_Tests.csv")


def _seed_path(system: str) -> Path:
    if system == "IEEE33":
        return resolve_path("seeds/ieee33_seeds.csv")
    if system == "IEEE69":
        return resolve_path("seeds/ieee69_seeds.csv")
    return resolve_path("seeds/baituf8_seeds.csv")


def action_show_config(system: str) -> str:
    mapped = SYSTEM_ALIAS[system]
    config_file = {
        "IEEE33": "config/ieee33.yaml",
        "IEEE69": "config/ieee69.yaml",
        "BaituF8": "config/baituf8_redacted.yaml",
    }[mapped]
    data = read_yaml(config_file)
    return dump_json(data)


def action_show_seeds(system: str) -> str:
    mapped = SYSTEM_ALIAS[system]
    rows = read_csv_rows(_seed_path(mapped))
    return dump_json(rows)


def action_summarize(system: str) -> str:
    mapped = SYSTEM_ALIAS[system]
    rows = read_csv_rows(_summary_path())
    picked = [summarize_row(r) for r in rows if r.get("system") == mapped]
    return dump_json(picked)


def action_fairness_check(system: str) -> str:
    mapped = SYSTEM_ALIAS[system]
    rows = read_csv_rows(resolve_path("results/fairness_check/pf_budget_summary.csv"))
    by_system = [r for r in rows if r.get("system") == mapped]
    checks: List[Dict[str, object]] = []
    for r in by_system:
        max_pf = float(r.get("max_pf_calls", 0.0))
        budget = float(r.get("budget", 0.0))
        checks.append(
            {
                "system": mapped,
                "algorithm": r.get("algorithm"),
                "max_pf_calls": max_pf,
                "budget": budget,
                "pass": max_pf <= budget,
            }
        )
    return dump_json(checks)


def action_rebuild_tables(output_dir: str) -> str:
    """基于公开资产重建关键表（不重跑实验）。"""
    out = resolve_path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    table_a = read_csv_rows(_table_a_path())
    table_b = read_csv_rows(_table_b_path())
    table_c = read_csv_rows(_summary_path())
    table_d = read_csv_rows(_table_d_path())

    write_csv_rows(out / "Table_A_System_and_Config.csv", table_a)
    write_csv_rows(out / "Table_B_Algorithm_Settings.csv", table_b)
    write_csv_rows(out / "Table_C_Performance_Summary.csv", table_c)
    write_csv_rows(out / "Table_D_Statistical_Tests.csv", table_d)

    demo_constraint = check_voltage_limits(ConstraintInput(voltage_min_pu=0.948, voltage_max_pu=1.043))

    return dump_json(
        {
            "output_dir": str(out),
            "tables": [
                "Table_A_System_and_Config.csv",
                "Table_B_Algorithm_Settings.csv",
                "Table_C_Performance_Summary.csv",
                "Table_D_Statistical_Tests.csv",
            ],
            "algorithm_interface_snapshot": {
                "GA": ga_config(),
                "PSO": pso_config(),
                "DE": de_config(),
                "GA-PSO": gapso_config(),
                "NSGA-III": nsga3_config(),
                "MOEA/D": moead_config(),
            },
            "constraint_demo": demo_constraint,
            "note": "Rebuilt from existing public files only. No experiment rerun performed.",
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="公开最小复现 CLI")
    parser.add_argument(
        "--system",
        default="IEEE33",
        choices=["IEEE33", "IEEE69", "BaituF8-redacted"],
        help="目标系统",
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["show-config", "show-seeds", "summarize", "fairness-check", "rebuild-tables"],
        help="执行动作",
    )
    parser.add_argument("--output", default="results", help="动作为 rebuild-tables 时的输出目录")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "show-config":
        print(action_show_config(args.system))
        return
    if args.action == "show-seeds":
        print(action_show_seeds(args.system))
        return
    if args.action == "summarize":
        print(action_summarize(args.system))
        return
    if args.action == "fairness-check":
        print(action_fairness_check(args.system))
        return
    if args.action == "rebuild-tables":
        print(action_rebuild_tables(args.output))
        return

    raise ValueError(f"Unsupported action: {args.action}")


if __name__ == "__main__":
    main()

