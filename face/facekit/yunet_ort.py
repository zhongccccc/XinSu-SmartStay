"""YuNet 检测器（onnxruntime 版）。

替换 OpenCV 的 cv2.FaceDetectorYN：OpenCV 4.6 无法加载 2023mar 版 YuNet，
会抛 "Layer with requested id=-1 not found"。这里直接用 onnxruntime 推理，
解码逻辑与 OpenCV 官方实现一致（cls/obj 取几何平均，宽高取 exp）。

接口与 detector.YuNetDetector 完全一致，可直接替换。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .detector import DetectedFace


def _nms(boxes: np.ndarray, scores: np.ndarray, iou_thr: float) -> list[int]:
    if len(boxes) == 0:
        return []
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = np.maximum(0.0, x2 - x1) * np.maximum(0.0, y2 - y1)
    order = scores.argsort()[::-1]
    keep = []
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
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        iou = inter / np.maximum(1e-9, areas[i] + areas[rest] - inter)
        order = rest[iou <= iou_thr]
    return keep


@dataclass
class _Raw:
    box: np.ndarray
    score: float
    kps: np.ndarray


class YuNetORTDetector:
    """与 YuNetDetector 同接口，用 onnxruntime 跑 ONNX 模型。"""

    def __init__(
        self,
        model_path: str | Path,
        input_size: int = 640,
        conf_threshold: float = 0.6,
        iou_threshold: float = 0.45,
        max_faces: int = 5,
        providers: list[str] | None = None,
        num_threads: int = 4,
    ) -> None:
        import onnxruntime as ort

        so = ort.SessionOptions()
        so.intra_op_num_threads = int(num_threads)
        so.log_severity_level = 3
        self.session = ort.InferenceSession(
            str(model_path), so, providers=providers or ["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        shape = self.session.get_inputs()[0].shape
        # 模型输入是固定的 640x640
        self.size = int(shape[2]) if isinstance(shape[2], int) else int(input_size)
        self.conf_threshold = float(conf_threshold)
        self.iou_threshold = float(iou_threshold)
        self.max_faces = int(max_faces)

    # ---------- 预处理 ----------
    def _preprocess(self, bgr: np.ndarray):
        h, w = bgr.shape[:2]
        s = min(self.size / w, self.size / h)
        nw, nh = max(1, int(round(w * s))), max(1, int(round(h * s)))
        resized = cv2.resize(bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
        canvas = np.zeros((self.size, self.size, 3), dtype=np.uint8)
        canvas[:nh, :nw] = resized          # 左上角对齐，右下补 0
        blob = canvas.astype(np.float32).transpose(2, 0, 1)[None, ...]
        return np.ascontiguousarray(blob), s

    # ---------- 解码 ----------
    def detect(self, bgr: np.ndarray) -> list[DetectedFace]:
        h, w = bgr.shape[:2]
        blob, scale = self._preprocess(bgr)
        outs = self.session.run(None, {self.input_name: blob})
        named = {o.name: v for o, v in zip(self.session.get_outputs(), outs)}

        boxes, scores, kpss = [], [], []
        for stride in (8, 16, 32):
            cols = self.size // stride
            cls = named[f"cls_{stride}"][0].reshape(-1)
            obj = named[f"obj_{stride}"][0].reshape(-1)
            bbox = named[f"bbox_{stride}"][0].reshape(-1, 4)
            kps = named[f"kps_{stride}"][0].reshape(-1, 10)

            score = np.sqrt(np.clip(cls, 0, 1) * np.clip(obj, 0, 1))
            idx = np.where(score >= self.conf_threshold)[0]
            if idx.size == 0:
                continue

            xs = (np.arange(cols) + 0.5) * stride
            ys = (np.arange(cols) + 0.5) * stride
            grid_x, grid_y = np.meshgrid(xs, ys)
            grid_x = grid_x.reshape(-1)[idx]
            grid_y = grid_y.reshape(-1)[idx]

            b = bbox[idx]
            cx = grid_x + b[:, 0] * stride
            cy = grid_y + b[:, 1] * stride
            bw = np.exp(b[:, 2]) * stride
            bh = np.exp(b[:, 3]) * stride

            boxes.append(np.stack([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], 1))
            scores.append(score[idx])

            k = kps[idx]
            pts = np.empty((idx.size, 5, 2), np.float32)
            for i in range(5):
                pts[:, i, 0] = grid_x + k[:, 2 * i] * stride
                pts[:, i, 1] = grid_y + k[:, 2 * i + 1] * stride
            kpss.append(pts)

        if not boxes:
            return []

        boxes = np.concatenate(boxes).astype(np.float32)
        scores = np.concatenate(scores).astype(np.float32)
        kpss = np.concatenate(kpss).astype(np.float32)

        keep = _nms(boxes, scores, self.iou_threshold)[: self.max_faces]
        out: list[DetectedFace] = []
        for i in keep:
            box = boxes[i] / scale
            pts = kpss[i] / scale
            box[[0, 2]] = np.clip(box[[0, 2]], 0, w)
            box[[1, 3]] = np.clip(box[[1, 3]], 0, h)
            out.append(DetectedFace(box=box.astype(np.float32),
                                    score=float(scores[i]),
                                    kps=pts.astype(np.float32)))
        out.sort(key=lambda d: (d.box[2] - d.box[0]) * (d.box[3] - d.box[1]), reverse=True)
        return out


class YuNetORTRefiner:
    """给 YOLOv5-face 补关键点用（接口与 detector.LandmarkRefiner 一致）。"""

    def __init__(self, model_path: str | Path, size: int = 640, conf: float = 0.3):
        self.det = YuNetORTDetector(model_path, input_size=size, conf_threshold=conf)

    def refine(self, bgr: np.ndarray, box):
        faces = self.det.detect(bgr)
        for f in faces:
            if f.kps is not None:
                return f.kps
        return None
