"""ArcFace（MobileFaceNet, 112x112 -> 128 维）特征提取。

注意：官方 arcface_mobilefacenet_cut 输出 128 维、且未做 L2 归一化（实测范数 ≈ 2.96），
所以归一化必须在外部做，否则余弦相似度会被模长带偏。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .io_utils import to_nchw_rgb


class ArcFaceEmbedder:
    def __init__(
        self,
        model_path: str | Path,
        providers: list[str] | None = None,
        num_threads: int = 4,
        input_size: int = 112,
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

    @property
    def dim(self) -> int:
        shape = self.session.get_outputs()[0].shape
        return int(shape[-1]) if isinstance(shape[-1], int) else 128

    def embed(self, aligned_bgr: np.ndarray) -> np.ndarray:
        if aligned_bgr.shape[0] != self.input_size or aligned_bgr.shape[1] != self.input_size:
            import cv2

            aligned_bgr = cv2.resize(aligned_bgr, (self.input_size, self.input_size))

        # 官方预处理：(x/255 - 0.5) / 0.5，RGB，NCHW
        x = to_nchw_rgb(aligned_bgr, scale=1.0 / 255.0)
        x = (x - 0.5) / 0.5
        out = self.session.run(None, {self.input_name: x.astype(np.float32)})[0][0]
        out = np.asarray(out, np.float32)
        norm = float(np.linalg.norm(out))
        return out / norm if norm > 1e-12 else out

    def embed_many(self, aligned_list: list[np.ndarray]) -> np.ndarray:
        if not aligned_list:
            return np.zeros((0, self.dim), np.float32)
        return np.stack([self.embed(a) for a in aligned_list]).astype(np.float32)
