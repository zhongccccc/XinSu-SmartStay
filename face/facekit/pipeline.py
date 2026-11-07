"""端到端比对流程。

一次核验：
  身份证芯片照 --检测--> 对齐 --> ArcFace --> 单位向量
  现场抓拍多帧 --检测--> 质量门控 --> 对齐 --> ArcFace --> 单位向量
  逐帧余弦 --> 中位数 --> 双阈值 --> pass / review / retry
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from .align import align_face
from .config import Config
from .detector import build_detector
from .embedder import ArcFaceEmbedder
from .matcher import Decision, cosine, decide
from .quality import QualityReport, assess_quality, pose_metrics


@dataclass
class Extraction:
    aligned: np.ndarray
    embedding: np.ndarray
    quality: QualityReport
    pose: dict
    detect_ms: float
    embed_ms: float


@dataclass
class FrameResult:
    index: int
    score: float | None = None
    quality: QualityReport | None = None
    pose: dict = field(default_factory=dict)
    error: str | None = None


@dataclass
class VerifyResult:
    decision: str
    score: float
    id_score: float | None
    frames: list[FrameResult]
    detail: Decision | None
    reason: str = ""
    latency_ms: dict = field(default_factory=dict)
    id_quality: QualityReport | None = None

    def as_dict(self) -> dict:
        return {
            "decision": self.decision,
            "score": round(self.score, 4),
            "reason": self.reason,
            "id_quality": self.id_quality.as_dict() if self.id_quality else None,
            "frames": [
                {
                    "index": f.index,
                    "score": None if f.score is None else round(f.score, 4),
                    "quality": f.quality.as_dict() if f.quality else None,
                    "pose": f.pose,
                    "error": f.error,
                }
                for f in self.frames
            ],
            "latency_ms": {k: round(v, 2) for k, v in self.latency_ms.items()},
        }


class FaceVerifier:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.detector = build_detector(cfg)
        self.embedder = ArcFaceEmbedder(
            cfg.resolve(cfg.models.arcface),
            providers=cfg.runtime.providers,
            num_threads=cfg.runtime.num_threads,
        )

    def _extract(self, bgr: np.ndarray, gate: bool, face=None) -> Extraction:
        """取图中最大人脸并提取特征；gate=True 时质量不合格抛 ValueError。

        face 非空时直接用它（跳过检测，用于多帧复用关键点）。
        """
        t0 = time.perf_counter()
        if face is None:
            faces = self.detector.detect(bgr)
            detect_ms = (time.perf_counter() - t0) * 1000
            if not faces:
                raise ValueError("未检测到人脸")
            face = faces[0]
        else:
            detect_ms = 0.0
        if face.kps is None:
            raise ValueError("未取得 5 点关键点，无法对齐")
        if face.kps is None:
            raise ValueError("未取得 5 点关键点，无法对齐")

        got = align_face(bgr, face.kps, size=112)
        if got is None:
            raise ValueError("对齐失败")
        aligned, _, err = got

        quality = assess_quality(
            aligned, float(face.box[2] - face.box[0]), err, face.kps, self.cfg.quality
        )
        if gate and not quality.ok:
            raise ValueError("质量不合格: " + "、".join(quality.reasons))

        t0 = time.perf_counter()
        emb = self.embedder.embed(aligned)
        embed_ms = (time.perf_counter() - t0) * 1000

        yaw, pitch, eye_dist = pose_metrics(face.kps)
        return Extraction(
            aligned=aligned,
            embedding=emb,
            quality=quality,
            pose={"yaw": round(yaw, 3), "pitch": round(pitch, 3), "eye_dist_px": round(eye_dist, 1)},
            detect_ms=detect_ms,
            embed_ms=embed_ms,
        )

    def embed_id_photo(self, bgr: np.ndarray) -> Extraction:
        """身份证芯片照取特征。证件照是标准正脸，质量门控只记录不拦截。"""
        return self._extract(bgr, gate=False)

    def verify(
        self,
        id_photo: np.ndarray,
        live_frames: list[np.ndarray],
        id_embedding: np.ndarray | None = None,
    ) -> VerifyResult:
        t_start = time.perf_counter()
        latency: dict[str, float] = {}

        # 1) 证件照特征
        id_quality = None
        if id_embedding is None:
            try:
                ext = self.embed_id_photo(id_photo)
                id_embedding = ext.embedding
                id_quality = ext.quality
                latency["id_ms"] = ext.detect_ms + ext.embed_ms
            except ValueError as exc:
                return VerifyResult("retry", 0.0, None, [], None, f"证件照处理失败: {exc}")

        # 2) 现场多帧
        frames: list[FrameResult] = []
        scores: list[float] = []
        detect_ms = embed_ms = 0.0
        for i, frame in enumerate(live_frames):
            fr = FrameResult(index=i)
            try:
                ext = self._extract(frame, gate=True)
                fr.score = cosine(id_embedding, ext.embedding)
                fr.quality = ext.quality
                fr.pose = ext.pose
                detect_ms += ext.detect_ms
                embed_ms += ext.embed_ms
                scores.append(fr.score)
            except ValueError as exc:
                fr.error = str(exc)
            frames.append(fr)

        n_eval = max(1, len(scores))
        latency["detect_ms_avg"] = detect_ms / n_eval
        latency["embed_ms_avg"] = embed_ms / n_eval

        # 3) 判定
        det = decide(scores, self.cfg.match)
        reason = {
            "pass": "比对通过",
            "review": "灰区，转人工复核",
            "retry": "未达阈值，提示重试",
        }[det.label]
        if not scores:
            reason = "现场照全部未通过质量门控，请调整光线/距离后重试"

        latency["total_ms"] = (time.perf_counter() - t_start) * 1000
        return VerifyResult(
            decision=det.label,
            score=det.score,
            id_score=None,
            frames=frames,
            detail=det,
            reason=reason,
            latency_ms=latency,
            id_quality=id_quality,
        )

    def verify_fast(self, id_photo: np.ndarray, live_frames: list[np.ndarray],
                    id_embedding: np.ndarray | None = None) -> VerifyResult:
        """快速版 verify：现场多帧里只在首帧和末帧做检测，中间帧复用关键点。

        一体机场景客人在 1~2 秒内基本不动，复用关键点能省掉一半检测耗时；
        复用帧仍要过质量门控（对齐误差、模糊、亮度），姿态偏了会被丢掉。
        """
        t_start = time.perf_counter()
        latency: dict[str, float] = {}
        id_quality = None

        if id_embedding is None:
            try:
                ext = self.embed_id_photo(id_photo)
                id_embedding = ext.embedding
                id_quality = ext.quality
                latency["id_ms"] = ext.detect_ms + ext.embed_ms
            except ValueError as exc:
                return VerifyResult("retry", 0.0, None, [], None, f"证件照处理失败: {exc}")

        frames: list[FrameResult] = []
        scores: list[float] = []
        detect_ms = embed_ms = 0.0
        ref = None
        n = len(live_frames)

        for i, frame in enumerate(live_frames):
            fr = FrameResult(index=i)
            try:
                need_detect = (ref is None) or (i == 0) or (i == n - 1)
                face = None
                if need_detect:
                    faces = self.detector.detect(frame)
                    if not faces:
                        raise ValueError("未检测到人脸")
                    ref = faces[0]
                    face = ref
                ext = self._extract(frame, gate=True, face=face)
                fr.score = cosine(id_embedding, ext.embedding)
                fr.quality = ext.quality
                fr.pose = ext.pose
                detect_ms += ext.detect_ms
                embed_ms += ext.embed_ms
                scores.append(fr.score)
            except ValueError as exc:
                fr.error = str(exc)
            frames.append(fr)

        n_eval = max(1, len(scores))
        latency["detect_ms_avg"] = detect_ms / n_eval
        latency["embed_ms_avg"] = embed_ms / n_eval

        det = decide(scores, self.cfg.match)
        reason = {
            "pass": "比对通过",
            "review": "灰区，转人工复核",
            "retry": "未达阈值，提示重试",
        }[det.label]
        if not scores:
            reason = "现场照全部未通过质量门控，请调整光线/距离后重试"

        latency["total_ms"] = (time.perf_counter() - t_start) * 1000
        return VerifyResult(
            decision=det.label,
            score=det.score,
            id_score=None,
            frames=frames,
            detail=det,
            reason=reason,
            latency_ms=latency,
            id_quality=id_quality,
        )
