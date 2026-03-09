#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一实验启动脚本。"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from extended_experiment import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行可复现实验")
    parser.add_argument("--config", required=True, help="配置文件路径")
    parser.add_argument("--out", required=True, help="输出目录")
    parser.add_argument("--mode", default="full", choices=["minimal", "full"], help="运行模式")
    parser.add_argument("--cache", default="on", choices=["on", "off"], help="缓存开关")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    run_pipeline(
        config_path=Path(args.config),
        out_dir=Path(args.out),
        mode=args.mode,
        cache_mode=args.cache,
        argv=(argv if argv is not None else os.sys.argv[1:]),
    )


if __name__ == "__main__":
    main(sys.argv[1:])

