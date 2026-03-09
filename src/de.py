"""DE 接口模块（公开最小复现仓库）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class DEConfig:
    """DE 关键超参数。"""

    population: int = 24
    iterations: int = 55
    F: float = 0.5
    CR: float = 0.8


def export_config_dict(cfg: DEConfig | None = None) -> Dict[str, float | int]:
    """导出配置字典。"""
    c = cfg or DEConfig()
    return {
        "population": c.population,
        "iterations": c.iterations,
        "F": c.F,
        "CR": c.CR,
    }

