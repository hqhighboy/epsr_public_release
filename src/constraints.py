"""约束检查模块（公开最小复现接口）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ConstraintInput:
    """约束输入。"""

    voltage_min_pu: float
    voltage_max_pu: float
    v_lower: float = 0.95
    v_upper: float = 1.05


def check_voltage_limits(inp: ConstraintInput) -> Dict[str, float]:
    """检查电压上下限违约量。"""
    low_violation = max(0.0, inp.v_lower - inp.voltage_min_pu)
    high_violation = max(0.0, inp.voltage_max_pu - inp.v_upper)
    return {
        "low_violation": low_violation,
        "high_violation": high_violation,
        "total_violation": low_violation + high_violation,
    }


def is_feasible(total_violation: float, eps: float = 1e-9) -> bool:
    """是否可行。"""
    return float(total_violation) <= eps

