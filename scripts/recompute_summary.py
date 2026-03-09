#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 runs.jsonl 重算 summary，并输出一致性报告。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from extended_experiment import recompute_summary_from_records


def load_runs(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="重算summary")
    parser.add_argument("--runs", required=True, help="runs.jsonl路径")
    parser.add_argument("--summary", required=True, help="已有summary.json路径")
    parser.add_argument("--out_summary", required=True, help="重算summary输出路径")
    parser.add_argument("--report", required=True, help="一致性报告路径")
    args = parser.parse_args()

    runs_path = Path(args.runs)
    summary_path = Path(args.summary)
    out_summary_path = Path(args.out_summary)
    report_path = Path(args.report)

    rows = load_runs(runs_path)
    recomputed = recompute_summary_from_records(rows)
    out_summary_path.write_text(json.dumps(recomputed, ensure_ascii=False, indent=2), encoding="utf-8")

    existing = json.loads(summary_path.read_text(encoding="utf-8"))
    same = json.dumps(existing, ensure_ascii=False, sort_keys=True) == json.dumps(
        recomputed, ensure_ascii=False, sort_keys=True
    )

    lines = [
        "# recompute_summary_report",
        "",
        f"- same: {same}",
        f"- runs_path: {runs_path}",
        f"- summary_path: {summary_path}",
        f"- recomputed_path: {out_summary_path}",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

