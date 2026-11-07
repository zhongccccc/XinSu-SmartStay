"""5 点相似变换对齐到 ArcFace 112x112 模板。

模板取自 SpacemiT 官方 align_face.cpp（与 buffalo_l 一致），不能随便改：
模型训练时就用的这个坐标系，模板不一致等于人为增加域差异。
"""

from __future__ import annotations

import cv2
import numpy as np

# ArcFace / buffalo_l 标准 5 点模板（112x112）
ARC_TEMPLATE_112 = np.array(
    [
        [38.2946, 51.6963],  # 左眼
        [73.5318, 51.5014],  # 右眼
        [56.0252, 71.7366],  # 鼻尖
        [41.5493, 92.3655],  # 左嘴角
        [70.7299, 92.2041],  # 右嘴角
    ],
    dtype=np.float32,
)


def similarity_transform(src: np.ndarray, dst: np.ndarray) -> np.ndarray | None:
    """闭式解求相似变换（只含 scale/rotation/translation），返回 2x3 矩阵。

    比 cv2.estimateAffinePartial2D 稳定：5 点正好定解，不需要 RANSAC。
    """
    src = np.asarray(src, np.float64).reshape(5, 2)
    dst = np.asarray(dst, np.float64).reshape(5, 2)
    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)
    src_c = src - src_mean
    dst_c = dst - dst_mean

    src_var = (src_c**2).sum()
    if src_var < 1e-6:
        return None
    a = (dst_c * src_c).sum() / src_var
    b = (dst_c[:, 1] * src_c[:, 0] - dst_c[:, 0] * src_c[:, 1]).sum() / src_var

    m = np.array(
        [
            [a, -b, dst_mean[0] - a * src_mean[0] + b * src_mean[1]],
            [b, a, dst_mean[1] - b * src_mean[0] - a * src_mean[1]],
        ],
        dtype=np.float64,
    )
    return m


def align_face(
    bgr: np.ndarray, kps: np.ndarray, size: int = 112
) -> tuple[np.ndarray, np.ndarray, float] | None:
    """按 5 点把脸摆正，返回 (对齐图, 2x3 矩阵, 平均重投影误差)。

    重投影误差是很好用的姿态代理指标：正脸通常 < 2px，明显侧脸/低头会到 4px 以上。
    """
    if kps is None or len(kps) != 5:
        return None
    dst = ARC_TEMPLATE_112 * (size / 112.0)
    m = similarity_transform(kps, dst)
    if m is None:
        return None

    aligned = cv2.warpAffine(
        bgr, m, (size, size), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )
    warped = (np.asarray(kps, np.float64) @ m[:, :2].T) + m[:, 2]
    err = float(np.linalg.norm(warped - dst, axis=1).mean())
    return aligned, m.astype(np.float32), err
