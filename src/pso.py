"""PSO 接口模块（公开最小复现仓库）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class PSOConfig:
    """PSO 关键超参数。"""

    population: int = 24
    iterations: int = 55
    w_max: float = 0.9
    w_min: float = 0.4
    c1: float = 1.8
    c2: float = 1.8


def inertia_at(iter_idx: int, iterations: int, w_max: float = 0.9, w_min: float = 0.4) -> float:
    """线性递减惯性权重。"""
    if iterations <= 1:
        return float(w_min)
    return float(w_max - (w_max - w_min) * (iter_idx / max(1, iterations - 1)))


def export_config_dict(cfg: PSOConfig | None = None) -> Dict[str, float | int]:
    """导出配置字典。"""
    c = cfg or PSOConfig()
    return {
        "population": c.population,
        "iterations": c.iterations,
        "w_max": c.w_max,
        "w_min": c.w_min,
        "c1": c.c1,
        "c2": c.c2,
    }

