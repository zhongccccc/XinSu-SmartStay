"""配置对象：从 config.yaml 读，带完整默认值。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ModelsCfg:
    detector: str = "yunet"
    yunet: str = "models/face_detection_yunet_2023mar.onnx"
    yolov5face: str = "models/yolov5n-face_320_cut.q.onnx"
    arcface: str = "models/arcface_mobilefacenet_cut.q.onnx"


@dataclass
class RuntimeCfg:
    providers: list[str] = field(default_factory=lambda: ["CPUExecutionProvider"])
    num_threads: int = 4


@dataclass
class DetectorCfg:
    input_size: int = 320
    conf_threshold: float = 0.6
    iou_threshold: float = 0.45
    max_faces: int = 5


@dataclass
class QualityCfg:
    min_face_px: float = 160.0
    blur_min: float = 35.0
    brightness_min: float = 60.0
    brightness_max: float = 200.0
    align_err_max: float = 6.0
    yaw_max: float = 0.15
    pitch_min: float = 0.30
    pitch_max: float = 0.70


@dataclass
class MatchCfg:
    t_high: float = 0.45
    t_low: float = 0.32
    aggregate: str = "median"
    min_valid_frames: int = 2


@dataclass
class CaptureCfg:
    width: int = 1280
    height: int = 720
    burst: int = 4
    burst_interval_ms: int = 120
    warmup_frames: int = 8


@dataclass
class StoreCfg:
    embed_db: str = "data/embeddings.db"
    audit_log: str = "data/verify_audit.jsonl"
    hash_salt: str = "change-me-per-site"


@dataclass
class Config:
    models: ModelsCfg = field(default_factory=ModelsCfg)
    runtime: RuntimeCfg = field(default_factory=RuntimeCfg)
    detector: DetectorCfg = field(default_factory=DetectorCfg)
    quality: QualityCfg = field(default_factory=QualityCfg)
    match: MatchCfg = field(default_factory=MatchCfg)
    capture: CaptureCfg = field(default_factory=CaptureCfg)
    store: StoreCfg = field(default_factory=StoreCfg)
    root: Path = field(default_factory=Path.cwd)

    @classmethod
    def load(cls, path: str | Path = "config.yaml") -> "Config":
        p = Path(path)
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        cfg = cls(
            models=ModelsCfg(**raw.get("models", {})),
            runtime=RuntimeCfg(**raw.get("runtime", {})),
            detector=DetectorCfg(**raw.get("detector", {})),
            quality=QualityCfg(**raw.get("quality", {})),
            match=MatchCfg(**raw.get("match", {})),
            capture=CaptureCfg(**raw.get("capture", {})),
            store=StoreCfg(**raw.get("store", {})),
            root=p.resolve().parent,
        )
        return cfg

    def resolve(self, rel: str) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else (self.root / p)
