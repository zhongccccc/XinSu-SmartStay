"""合成"现场抓拍"：把证件照摆到 720p 画面里并加透视/噪声/模糊。

只用于在没有真机时跑通链路和摸条件边界，**不能**用来定阈值。
"""

from __future__ import annotations

import cv2
import numpy as np


def _yaw_homography(width: int, height: int, yaw_deg: float, focal_ratio: float = 1.4) -> np.ndarray:
    """绕竖直轴转 yaw_deg 度的「转台」透视，比梯形 keystone 更接近真实侧脸。"""
    f = focal_ratio * max(width, height)
    k = np.array([[f, 0, width / 2], [0, f, height / 2], [0, 0, 1]], np.float64)
    t = np.deg2rad(yaw_deg)
    rot = np.array(
        [[np.cos(t), 0, np.sin(t)], [0, 1, 0], [-np.sin(t), 0, np.cos(t)]], np.float64
    )
    return k @ rot @ np.linalg.inv(k)


def make_capture(
    src: np.ndarray,
    width: int = 1280,
    height: int = 720,
    face_height: float = 280.0,
    yaw: float = 5.0,
    brightness: float = 0.85,
    blur: float = 2.0,
    noise: float = 6.0,
    seed: int = 0,
    background: int = 70,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    sh, sw = src.shape[:2]

    face_h_src = sh * 0.45  # 证件照里人脸大致占 45% 高
    scale = face_height / face_h_src
    portrait = cv2.resize(src, (int(round(sw * scale)), int(round(sh * scale))))

    canvas = np.full((height, width, 3), background, np.uint8)
    fh, fw = portrait.shape[:2]
    x0 = max(0, (width - fw) // 2)
    y0 = max(0, min(int(height * 0.5 - fh * 0.55), height - fh))
    canvas[y0 : y0 + min(fh, height), x0 : x0 + min(fw, width)] = portrait[: min(fh, height), : min(fw, width)]

    if abs(yaw) > 1e-3:
        m = _yaw_homography(width, height, yaw)
        canvas = cv2.warpPerspective(canvas, m, (width, height), borderValue=(background,) * 3)

    if blur > 0:
        canvas = cv2.GaussianBlur(canvas, (0, 0), blur)
    canvas = np.clip(canvas.astype(np.float32) * brightness, 0, 255)
    if noise > 0:
        canvas = canvas + rng.normal(0, noise, canvas.shape).astype(np.float32)
    return np.clip(canvas, 0, 255).astype(np.uint8)
