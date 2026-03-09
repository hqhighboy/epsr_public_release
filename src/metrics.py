"""指标与统计辅助函数。"""

from __future__ import annotations

import statistics
from typing import Iterable, List


def mean(values: Iterable[float]) -> float:
    """均值。"""
    vals = list(values)
    return float(sum(vals) / len(vals)) if vals else 0.0


def std(values: Iterable[float]) -> float:
    """总体标准差。"""
    vals = list(values)
    if len(vals) <= 1:
        return 0.0
    return float(statistics.pstdev(vals))


def median(values: Iterable[float]) -> float:
    """中位数。"""
    vals = list(values)
    if not vals:
        return 0.0
    vals_sorted: List[float] = sorted(float(v) for v in vals)
    n = len(vals_sorted)
    mid = n // 2
    if n % 2 == 1:
        return vals_sorted[mid]
    return 0.5 * (vals_sorted[mid - 1] + vals_sorted[mid])

