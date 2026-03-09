"""GA 接口模块（公开最小复现仓库）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class GAConfig:
    """GA 关键超参数（与论文复现实验口径一致）。"""

    population: int = 24
    iterations: int = 55
    crossover_prob: float = 0.85
    mutation_prob: float = 0.15


def get_interface_note() -> str:
    """返回模块用途说明。"""
    return (
        "GA 模块在该公开仓库中提供复现实验接口与参数口径，"
        "用于结果表复核与配置对齐，不在此处重跑完整大规模实验。"
    )


def export_config_dict(cfg: GAConfig | None = None) -> Dict[str, float | int]:
    """导出配置字典。"""
    c = cfg or GAConfig()
    return {
        "population": c.population,
        "iterations": c.iterations,
        "crossover_prob": c.crossover_prob,
        "mutation_prob": c.mutation_prob,
    }

