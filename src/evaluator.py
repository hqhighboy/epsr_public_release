"""评估接口（复现实验公开最小版）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ObjectiveWeights:
    """目标权重。"""

    alpha: float
    beta: float
    gamma: float


def weighted_fitness(norm_loss: float, norm_vdev: float, norm_cost: float, penalty: float, w: ObjectiveWeights) -> float:
    """按论文配置计算标量 fitness。"""
    return float(w.alpha * norm_loss + w.beta * norm_vdev + w.gamma * norm_cost + penalty)


def summarize_row(row: Dict[str, str]) -> Dict[str, float | str]:
    """将结果行中的核心字段抽取为摘要。"""
    return {
        "system": row.get("system", ""),
        "algorithm": row.get("algorithm", ""),
        "mean_fitness": float(row.get("mean_fitness", 0.0)),
        "success_rate": float(row.get("success_rate", 0.0)),
        "mean_pf_calls": float(row.get("mean_pf_calls", 0.0)),
    }

