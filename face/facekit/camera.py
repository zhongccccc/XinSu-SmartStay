"""摄像头采集（K1 上用 V4L2 / MIPI-CSI）。

IMX219 通过 ISP 后一般呈现为 /dev/video*，OpenCV 指定 CAP_V4L2 最稳。
一体机场景关键点：先丢几帧等 AE/AWB 收敛，再连拍多帧供质量筛选。
"""

from __future__ import annotations

import time

import cv2
import numpy as np


class Camera:
    def __init__(
        self,
        index: int = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
        backend: int | None = None,
        warmup_frames: int = 8,
    ) -> None:
        self.width = int(width)
        self.height = int(height)
        backend = cv2.CAP_V4L2 if backend is None else backend
        self.cap = cv2.VideoCapture(index, backend)
        if not self.cap.isOpened():  # 部分平台 V4L2 打不开，退回默认后端
            self.cap.release()
            self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头 {index}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        for _ in range(max(0, warmup_frames)):
            self.cap.read()

    @property
    def actual_size(self) -> tuple[int, int]:
        return (
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def read(self) -> np.ndarray | None:
        ok, frame = self.cap.read()
        return frame if ok else None

    def preview(self) -> np.ndarray | None:
        """实时预览用：丢弃积压帧，保证拿到的是当前画面。"""
        self.cap.grab()
        return self.read()

    def burst(self, n: int = 4, interval_ms: int = 120) -> list[np.ndarray]:
        frames: list[np.ndarray] = []
        for _ in range(n):
            frame = self.read()
            if frame is not None:
                frames.append(frame)
            time.sleep(interval_ms / 1000.0)
        return frames

    def release(self) -> None:
        self.cap.release()

    def __enter__(self) -> "Camera":
        return self

    def __exit__(self, *exc) -> None:
        self.release()
