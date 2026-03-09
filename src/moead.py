"""MOEA/D 接口模块（公开最小复现仓库）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class MOEADConfig:
    """MOEA/D 参数摘要。"""

    population: int = 24
    iterations: int = 55
    neighborhood: int = 10
    de_F: float = 0.5
    de_CR: float = 0.8


def interface_status() -> Dict[str, str]:
    """声明当前公开仓库对 MOEA/D 的提供范围。"""
    return {
        "status": "interface-placeholder",
        "note": (
            "当前仓库提供复现实验接口/占位实现路径与参数口径，"
            "公开复核以结果表复核为主，不伪造新实验结果。"
        ),
    }


def export_config_dict(cfg: MOEADConfig | None = None) -> Dict[str, float | int | str]:
    """导出配置字典。"""
    c = cfg or MOEADConfig()
    return {
        "population": c.population,
        "iterations": c.iterations,
        "neighborhood": c.neighborhood,
        "de_F": c.de_F,
        "de_CR": c.de_CR,
        **interface_status(),
    }

