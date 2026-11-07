"""抓拍质量门控。

真正的通过率瓶颈在这里，不在模型。一张糊的、逆光的、只占 100 像素宽的脸，
再怎么调阈值也救不回来——宁可直接提示重拍。

姿态用的是「鼻尖相对眼-嘴中线的偏移」，不是对齐残差：
相似变换只有 4 个自由度，无论侧多少度都能把 5 点拟合得很贴，残差不能反映姿态。
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from .config import QualityCfg


@dataclass
class QualityReport:
    ok: bool
    face_px: float
    blur: float
    brightness: float
    align_err: float
    yaw: float = 0.0
    pitch: float = 0.0
    eye_dist: float = 0.0
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "face_px": round(self.face_px, 1),
            "blur": round(self.blur, 2),
            "brightness": round(self.brightness, 1),
            "align_err": round(self.align_err, 2),
            "yaw": round(self.yaw, 3),
            "pitch": round(self.pitch, 3),
            "reasons": self.reasons,
        }


def laplacian_variance(gray: np.ndarray) -> float:
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def pose_metrics(kps: np.ndarray) -> tuple[float, float, float]:
    """返回 (yaw 代理, pitch 代理, 瞳距像素)。

    yaw:   0 附近是正脸；|yaw| > 0.15 已能看出明显侧脸（鼻子偏向一侧）。
    pitch: 正脸大致 0.42~0.58；明显低头/仰头会超出这个范围。
    """
    kps = np.asarray(kps, np.float32).reshape(5, 2)
    eye_mid = (kps[0] + kps[1]) / 2.0
    eye_dist = float(np.linalg.norm(kps[1] - kps[0])) + 1e-6
    nose = kps[2]
    mouth_mid = (kps[3] + kps[4]) / 2.0

    yaw = float((nose[0] - eye_mid[0]) / eye_dist)
    denom = float(mouth_mid[1] - eye_mid[1]) + 1e-6
    pitch = float((nose[1] - eye_mid[1]) / denom)
    return yaw, pitch, eye_dist


def assess_quality(
    aligned_bgr: np.ndarray,
    face_box_w: float,
    align_err: float,
    kps: np.ndarray,
    cfg: QualityCfg,
) -> QualityReport:
    gray = cv2.cvtColor(aligned_bgr, cv2.COLOR_BGR2GRAY)
    blur = laplacian_variance(gray)
    brightness = float(gray.mean())
    yaw, pitch, eye_dist = pose_metrics(kps)

    reasons: list[str] = []
    if face_box_w < cfg.min_face_px:
        reasons.append(f"人脸太小({face_box_w:.0f}px<{cfg.min_face_px:.0f})")
    if blur < cfg.blur_min:
        reasons.append(f"图像模糊({blur:.0f}<{cfg.blur_min:.0f})")
    if brightness < cfg.brightness_min:
        reasons.append(f"过暗({brightness:.0f})")
    elif brightness > cfg.brightness_max:
        reasons.append(f"过曝({brightness:.0f})")
    if abs(yaw) > cfg.yaw_max:
        reasons.append(f"侧脸({yaw:+.2f})")
    if not (cfg.pitch_min <= pitch <= cfg.pitch_max):
        reasons.append(f"抬头/低头({pitch:.2f})")

    return QualityReport(
        ok=not reasons,
        face_px=float(face_box_w),
        blur=blur,
        brightness=brightness,
        align_err=float(align_err),
        yaw=yaw,
        pitch=pitch,
        eye_dist=eye_dist,
        reasons=reasons,
    )
