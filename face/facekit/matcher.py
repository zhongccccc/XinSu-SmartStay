"""比对判定：余弦相似度 + 双阈值 + 多帧聚合。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import MatchCfg


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, np.float32).ravel()
    b = np.asarray(b, np.float32).ravel()
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom > 1e-12 else 0.0


@dataclass
class Decision:
    label: str  # pass | review | retry
    score: float
    t_high: float
    t_low: float
    agree_ratio: float  # 通过阈值的帧占比，用于发现"平均分高但抖动大"的情况
    n_frames: int


def aggregate(scores: list[float], method: str = "median") -> float:
    if not scores:
        return 0.0
    arr = np.asarray(scores, np.float32)
    if method == "max":
        return float(arr.max())
    if method == "mean":
        return float(arr.mean())
    return float(np.median(arr))


def decide(scores: list[float], cfg: MatchCfg) -> Decision:
    """双阈值判定。

    * 中位数 >= t_high 且多数帧也过 t_high → pass
    * 中位数 <  t_low  → retry（提示重拍，不要直接拒绝）
    * 其余           → review（转前台人工，别让客人卡在机器前）
    """
    if not scores:
        return Decision("retry", 0.0, cfg.t_high, cfg.t_low, 0.0, 0)

    score = aggregate(scores, cfg.aggregate)
    agree = float(np.mean([s >= cfg.t_high for s in scores]))
    n = len(scores)

    if n < cfg.min_valid_frames:
        return Decision("retry", score, cfg.t_high, cfg.t_low, agree, n)
    if score >= cfg.t_high and agree >= 0.5:
        return Decision("pass", score, cfg.t_high, cfg.t_low, agree, n)
    if score >= cfg.t_low:
        return Decision("review", score, cfg.t_high, cfg.t_low, agree, n)
    return Decision("retry", score, cfg.t_high, cfg.t_low, agree, n)
