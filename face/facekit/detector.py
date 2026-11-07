"""人脸检测：框 + 5 点关键点。

两个检测器都经过实测：

* YuNet（OpenCV 内置，232 KB）——框和 5 点都准，默认用它。
* YOLOv5-face（SpacemiT Model Zoo 官方 INT8，2 MB）——框准（实测置信度 0.87，
  框与人工标注一致），但这个「cut」导出的关键点通道按官方 C++ 的两种公式都解不对，
  5 个点会挤在框中心。所以它只出框，关键点交给 YuNet 在小图上补（见 LandmarkRefiner）。

这样既保留了 YOLOv5-face 在 K1 上的速度优势，又不会让对齐质量拖垮比对精度。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .io_utils import LetterboxInfo, clip_box, letterbox, nms, to_nchw_rgb


@dataclass
class DetectedFace:
    box: np.ndarray  # xyxy，原图坐标
    score: float
    kps: np.ndarray | None = None  # 5x2，原图坐标
    landmarks_reliable: bool = True


# YOLOv5-face 官方 anchors（640 尺度，模型内部按 320 推理，解码与官方 C++ 一致）
_ANCHORS = np.array(
    [
        [[4, 5], [8, 10], [13, 16]],
        [[23, 29], [43, 55], [73, 105]],
        [[146, 217], [231, 300], [335, 433]],
    ],
    dtype=np.float32,
)
_STRIDES = (8, 16, 32)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


class YuNetDetector:
    """OpenCV 自带 YuNet：轻量、5 点稳定，适合一体机这种近距离正脸场景。"""

    def __init__(
        self,
        model_path: str | Path,
        input_size: int = 320,
        conf_threshold: float = 0.6,
        iou_threshold: float = 0.45,
        max_faces: int = 5,
    ) -> None:
        self.model_path = str(model_path)
        self.input_size = int(input_size)
        self.conf_threshold = float(conf_threshold)
        self.iou_threshold = float(iou_threshold)
        self.max_faces = int(max_faces)
        self._det = cv2.FaceDetectorYN.create(
            self.model_path, "", (self.input_size, self.input_size),
            self.conf_threshold, self.iou_threshold, self.max_faces,
        )

    def detect(self, bgr: np.ndarray) -> list[DetectedFace]:
        h, w = bgr.shape[:2]
        scale = self.input_size / max(h, w)
        if scale < 1.0:
            small = cv2.resize(bgr, (int(round(w * scale)), int(round(h * scale))), cv2.INTER_LINEAR)
        else:
            small = bgr
            scale = 1.0
        sh, sw = small.shape[:2]
        self._det.setInputSize((sw, sh))
        _, faces = self._det.detect(small)
        if faces is None:
            return []

        out: list[DetectedFace] = []
        for f in faces:
            x, y, bw, bh = f[:4] / scale
            kps = (f[4:14].reshape(5, 2) / scale).astype(np.float32)
            box = clip_box(np.array([x, y, x + bw, y + bh], np.float32), w, h)
            out.append(DetectedFace(box=box, score=float(f[14]), kps=kps))
        out.sort(key=lambda d: (d.box[2] - d.box[0]) * (d.box[3] - d.box[1]), reverse=True)
        return out


class YoloV5FaceDetector:
    """SpacemiT Model Zoo 的 yolov5n-face_320_cut.q.onnx：只负责出框。"""

    def __init__(
        self,
        model_path: str | Path,
        providers: list[str] | None = None,
        num_threads: int = 4,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        input_size: int = 320,
        refiner: "LandmarkRefiner | None" = None,
    ) -> None:
        import onnxruntime as ort

        so = ort.SessionOptions()
        so.intra_op_num_threads = int(num_threads)
        so.log_severity_level = 3
        self.session = ort.InferenceSession(
            str(model_path), so, providers=providers or ["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        self.input_size = int(input_size)
        self.conf_threshold = float(conf_threshold)
        self.iou_threshold = float(iou_threshold)
        self.refiner = refiner

    def detect(self, bgr: np.ndarray) -> list[DetectedFace]:
        h, w = bgr.shape[:2]
        canvas, info = letterbox(bgr, self.input_size)
        outs = self.session.run(None, {self.input_name: to_nchw_rgb(canvas)})

        boxes, scores = self._decode(outs, info)
        keep = nms(boxes, scores, self.iou_threshold)[:5]

        out: list[DetectedFace] = []
        for i in keep:
            box = clip_box(boxes[i], w, h)
            kps = None
            reliable = False
            if self.refiner is not None:
                kps = self.refiner.refine(bgr, box)
                reliable = kps is not None
            out.append(
                DetectedFace(box=box, score=float(scores[i]), kps=kps, landmarks_reliable=reliable)
            )
        out.sort(key=lambda d: (d.box[2] - d.box[0]) * (d.box[3] - d.box[1]), reverse=True)
        return out

    def _decode(self, outs: list[np.ndarray], info: LetterboxInfo) -> tuple[np.ndarray, np.ndarray]:
        all_boxes, all_scores = [], []
        for level, o in enumerate(outs):
            _, na, ny, nx, _ = o.shape
            p = o[0]  # (na, ny, nx, 16)
            gy, gx = np.meshgrid(np.arange(ny), np.arange(nx), indexing="ij")
            stride = _STRIDES[level]
            for a in range(na):
                q = p[a]
                score = _sigmoid(q[..., 4]) * _sigmoid(q[..., 15])
                mask = score > self.conf_threshold
                if not mask.any():
                    continue
                cx = (_sigmoid(q[..., 0]) * 2 - 0.5 + gx) * stride
                cy = (_sigmoid(q[..., 1]) * 2 - 0.5 + gy) * stride
                bw = (_sigmoid(q[..., 2]) * 2) ** 2 * _ANCHORS[level][a][0]
                bh = (_sigmoid(q[..., 3]) * 2) ** 2 * _ANCHORS[level][a][1]
                b = np.stack(
                    [cx[mask] - bw[mask] / 2, cy[mask] - bh[mask] / 2,
                     cx[mask] + bw[mask] / 2, cy[mask] + bh[mask] / 2],
                    axis=1,
                )
                all_boxes.append(info.to_original_boxes(b))
                all_scores.append(score[mask])
        if not all_boxes:
            return np.zeros((0, 4), np.float32), np.zeros((0,), np.float32)
        return (
            np.concatenate(all_boxes).astype(np.float32),
            np.concatenate(all_scores).astype(np.float32),
        )


class LandmarkRefiner:
    """用 YuNet 在检测框的局部放大图上取 5 点，避免大图里小脸检不到。"""

    def __init__(self, yunet_path: str | Path, margin: float = 0.35, size: int = 320) -> None:
        self.det = YuNetDetector(yunet_path, input_size=size, conf_threshold=0.5)
        self.margin = float(margin)

    def refine(self, bgr: np.ndarray, box: np.ndarray) -> np.ndarray | None:
        h, w = bgr.shape[:2]
        bw, bh = box[2] - box[0], box[3] - box[1]
        mx, my = bw * self.margin, bh * self.margin
        x1 = int(max(0, box[0] - mx))
        y1 = int(max(0, box[1] - my))
        x2 = int(min(w, box[2] + mx))
        y2 = int(min(h, box[3] + my))
        if x2 - x1 < 20 or y2 - y1 < 20:
            return None
        crop = bgr[y1:y2, x1:x2]
        faces = self.det.detect(crop)
        if not faces or faces[0].kps is None:
            return None
        kps = faces[0].kps + np.array([x1, y1], np.float32)
        return kps.astype(np.float32)


def build_detector(cfg) -> object:
    """按配置构建检测器。"""
    kind = (cfg.models.detector or "yunet").lower()
    if kind in {"yunet_ort", "yunet-ort", "ort"}:
        from .yunet_ort import YuNetORTDetector

        return YuNetORTDetector(
            cfg.resolve(cfg.models.yunet),
            conf_threshold=cfg.detector.conf_threshold,
            iou_threshold=cfg.detector.iou_threshold,
            max_faces=cfg.detector.max_faces,
            providers=cfg.runtime.providers,
            num_threads=cfg.runtime.num_threads,
        )
    if kind == "yunet":
        return YuNetDetector(
            cfg.resolve(cfg.models.yunet),
            input_size=cfg.detector.input_size,
            conf_threshold=cfg.detector.conf_threshold,
            iou_threshold=cfg.detector.iou_threshold,
            max_faces=cfg.detector.max_faces,
        )
    if kind in {"yolov5face", "yolo", "yolov5-face"}:
        refiner = LandmarkRefiner(cfg.resolve(cfg.models.yunet), size=cfg.detector.input_size)
        return YoloV5FaceDetector(
            cfg.resolve(cfg.models.yolov5face),
            providers=cfg.runtime.providers,
            num_threads=cfg.runtime.num_threads,
            conf_threshold=cfg.detector.conf_threshold,
            iou_threshold=cfg.detector.iou_threshold,
            input_size=cfg.detector.input_size,
            refiner=refiner,
        )
    raise ValueError(f"未知检测器: {cfg.models.detector}")
