"""NSGA-III 接口模块（公开最小复现仓库）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class NSGA3Config:
    """NSGA-III 参数摘要。"""

    population: int = 24
    iterations: int = 55
    ref_points: int = 12


def interface_status() -> Dict[str, str]:
    """声明当前公开仓库对 NSGA-III 的提供范围。"""
    return {
        "status": "interface-placeholder",
        "note": (
            "当前仓库提供复现实验接口/占位实现路径与参数口径，"
            "公开复核以结果表复核为主，不伪造新实验结果。"
        ),
    }


def export_config_dict(cfg: NSGA3Config | None = None) -> Dict[str, float | int | str]:
    """导出配置字典。"""
    c = cfg or NSGA3Config()
    return {
        "population": c.population,
        "iterations": c.iterations,
        "ref_points": c.ref_points,
        **interface_status(),
    }

