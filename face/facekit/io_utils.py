"""图像 IO 与几何工具。

两个坑：
1. Windows 上 cv2.imread 走 ANSI 接口，中文路径（例如 E:\\人脸配对\\原.png）会读失败，
   必须 np.fromfile + cv2.imdecode。
2. letterbox 的缩放/填充必须和目标检测框一一对应，否则框会偏移，这里统一封装。
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


def imread_unicode(path: str) -> np.ndarray:
    """读取任意路径（含中文）的图片，返回 BGR。失败抛 FileNotFoundError。"""
    buf = np.fromfile(path, dtype=np.uint8)
    if buf.size == 0:
        raise FileNotFoundError(path)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"无法解码图片: {path}")
    return img


def imwrite_unicode(path: str, img: np.ndarray) -> None:
    """写入任意路径（含中文）的图片。"""
    ok, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    if not ok:
        raise ValueError(f"编码失败: {path}")
    buf.tofile(path)


@dataclass(frozen=True)
class LetterboxInfo:
    """letterbox 的几何参数，把所有坐标换算回原图。"""

    scale: float
    pad_x: float
    pad_y: float

    def to_original(self, points: np.ndarray) -> np.ndarray:
        pts = np.asarray(points, dtype=np.float32).reshape(-1, 2)
        return (pts - np.array([self.pad_x, self.pad_y], np.float32)) / self.scale

    def to_original_boxes(self, boxes: np.ndarray) -> np.ndarray:
        boxes = np.asarray(boxes, dtype=np.float32).reshape(-1, 4)
        pad = np.array([self.pad_x, self.pad_y, self.pad_x, self.pad_y], np.float32)
        return (boxes - pad) / self.scale

    def to_letterboxed(self, points: np.ndarray) -> np.ndarray:
        pts = np.asarray(points, dtype=np.float32).reshape(-1, 2)
        return pts * self.scale + np.array([self.pad_x, self.pad_y], np.float32)


def letterbox(
    img: np.ndarray, size: int | tuple[int, int] = 320, color: int = 114
) -> tuple[np.ndarray, LetterboxInfo]:
    """等比缩放 + 居中灰边填充（与 SpacemiT demo / YOLOv5 预处理一致）。"""
    if isinstance(size, int):
        target_h = target_w = size
    else:
        target_h, target_w = size

    h, w = img.shape[:2]
    scale = min(target_w / w, target_h / h)
    nw, nh = int(round(w * scale)), int(round(h * scale))
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)

    canvas = np.full((target_h, target_w, 3), color, dtype=np.uint8)
    pad_x = (target_w - nw) // 2
    pad_y = (target_h - nh) // 2
    canvas[pad_y : pad_y + nh, pad_x : pad_x + nw] = resized
    return canvas, LetterboxInfo(scale, pad_x, pad_y)


def to_nchw_rgb(img_bgr: np.ndarray, scale: float = 1.0 / 255.0) -> np.ndarray:
    """BGR HWC uint8 -> RGB NCHW float32。"""
    x = img_bgr[:, :, ::-1].astype(np.float32) * scale
    return np.transpose(x, (2, 0, 1))[None]


def nms(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float) -> list[int]:
    """极简 NMS。boxes 为 xyxy，返回保留的下标（按分数降序）。"""
    if len(boxes) == 0:
        return []
    x1, y1, x2, y2 = boxes.T
    areas = np.maximum(0.0, x2 - x1) * np.maximum(0.0, y2 - y1)
    order = scores.argsort()[::-1]
    keep: list[int] = []
    while order.size > 0:
        i = int(order[0])
        keep.append(i)
        if order.size == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(x1[i], x1[rest])
        yy1 = np.maximum(y1[i], y1[rest])
        xx2 = np.minimum(x2[i], x2[rest])
        yy2 = np.minimum(y2[i], y2[rest])
        inter = np.maximum(0.0, xx2 - xx1) * np.maximum(0.0, yy2 - yy1)
        iou = inter / np.maximum(1e-9, areas[i] + areas[rest] - inter)
        order = rest[iou <= iou_threshold]
    return keep


def clip_box(box: np.ndarray, w: int, h: int) -> np.ndarray:
    x1, y1, x2, y2 = box.astype(np.float32)
    return np.array(
        [np.clip(x1, 0, w - 1), np.clip(y1, 0, h - 1), np.clip(x2, 0, w - 1), np.clip(y2, 0, h - 1)],
        dtype=np.float32,
    )
