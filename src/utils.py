"""公共复现仓库的通用工具函数。"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml


ROOT = Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    """返回 `paper-repro` 根目录。"""
    return ROOT


def resolve_path(path: str | Path) -> Path:
    """将相对路径解析为仓库内绝对路径。"""
    p = Path(path)
    if p.is_absolute():
        return p
    return ROOT / p


def read_yaml(path: str | Path) -> Dict[str, Any]:
    """读取 YAML 配置并返回字典。"""
    p = resolve_path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML 文件不是字典结构: {p}")
    return data


def read_csv_rows(path: str | Path) -> List[Dict[str, str]]:
    """读取 CSV 并返回字典行列表。"""
    p = resolve_path(path)
    with p.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    # 过滤可能由异常分隔产生的 None 键列，避免后续写回时报错
    cleaned: List[Dict[str, str]] = []
    for r in rows:
        if None in r:
            r = {k: v for k, v in r.items() if k is not None}
        cleaned.append(r)
    return cleaned


def write_csv_rows(path: str | Path, rows: Iterable[Dict[str, Any]], fieldnames: List[str] | None = None) -> None:
    """写出字典行到 CSV 文件。"""
    p = resolve_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    row_list = list(rows)

    if fieldnames is None:
        if not row_list:
            raise ValueError("空行集时必须显式提供 fieldnames")
        fieldnames = list(row_list[0].keys())

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(row_list)


def dump_json(value: Any) -> str:
    """以可读 JSON 字符串形式序列化对象。"""
    return json.dumps(value, ensure_ascii=False, indent=2)


def to_float(value: Any, default: float = 0.0) -> float:
    """稳健浮点转换。"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
