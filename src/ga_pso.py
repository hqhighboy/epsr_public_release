"""GA-PSO 接口模块（公开最小复现仓库）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class GAPSOConfig:
    """GA-PSO 混合超参数摘要。"""

    population: int = 24
    iterations: int = 55
    ga_mutation_prob: float = 0.15
    hybrid_mutation_scale: float = 0.7
    pso_w_max: float = 0.9
    pso_w_min: float = 0.4
    pso_c1: float = 1.8
    pso_c2: float = 1.8


def effective_mutation_prob(cfg: GAPSOConfig | None = None) -> float:
    """返回混合阶段有效变异概率。"""
    c = cfg or GAPSOConfig()
    return float(c.ga_mutation_prob * c.hybrid_mutation_scale)


def export_config_dict(cfg: GAPSOConfig | None = None) -> Dict[str, float | int]:
    """导出配置字典。"""
    c = cfg or GAPSOConfig()
    return {
        "population": c.population,
        "iterations": c.iterations,
        "ga_mutation_prob": c.ga_mutation_prob,
        "hybrid_mutation_scale": c.hybrid_mutation_scale,
        "effective_mutation_prob": effective_mutation_prob(c),
        "pso_w_max": c.pso_w_max,
        "pso_w_min": c.pso_w_min,
        "pso_c1": c.pso_c1,
        "pso_c2": c.pso_c2,
    }

