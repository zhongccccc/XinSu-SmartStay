"""不依赖 pytest 的自检：python tests/test_core.py"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.align import ARC_TEMPLATE_112, align_face, similarity_transform  # noqa: E402
from facekit.config import MatchCfg  # noqa: E402
from facekit.io_utils import letterbox  # noqa: E402
from facekit.matcher import cosine, decide  # noqa: E402


def test_similarity_recovers_known_transform() -> None:
    theta = np.deg2rad(7.0)
    s = 1.8
    t = np.array([13.0, -21.0])
    r = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]) * s
    dst = ARC_TEMPLATE_112
    src = (dst - t) @ np.linalg.inv(r).T

    m = similarity_transform(src, dst)
    assert m is not None
    warped = src @ m[:, :2].T + m[:, 2]
    assert np.abs(warped - dst).max() < 1e-6


def test_align_reprojects_near_zero() -> None:
    img = np.zeros((200, 200, 3), np.uint8)
    kps = ARC_TEMPLATE_112 + np.array([20.0, 30.0], np.float32)
    got = align_face(img, kps, size=112)
    assert got is not None
    _, m, err = got
    assert err < 1e-3, err


def test_letterbox_roundtrip() -> None:
    img = np.zeros((480, 640, 3), np.uint8)
    canvas, info = letterbox(img, 320)
    assert canvas.shape == (320, 320, 3)
    pts = np.array([[100.0, 50.0], [640.0, 480.0]], np.float32)
    back = info.to_original(info.to_letterboxed(pts))
    assert np.abs(back - pts).max() < 1e-3


def test_cosine_and_dual_threshold() -> None:
    a = np.array([1.0, 0.0, 0.0], np.float32)
    b = np.array([1.0, 0.0, 0.0], np.float32)
    c = np.array([0.0, 1.0, 0.0], np.float32)
    assert abs(cosine(a, b) - 1.0) < 1e-6
    assert abs(cosine(a, c)) < 1e-6

    cfg = MatchCfg(t_high=0.45, t_low=0.32, min_valid_frames=2)
    assert decide([0.6, 0.55, 0.7], cfg).label == "pass"
    assert decide([0.4, 0.38], cfg).label == "review"
    assert decide([0.1, 0.2], cfg).label == "retry"
    # 帧数不足 -> retry
    assert decide([0.9], cfg).label == "retry"
    # 平均高但只有一帧过线 -> 不该直接 pass
    assert decide([0.9, 0.3, 0.28, 0.3], cfg).label != "pass"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all passed")
