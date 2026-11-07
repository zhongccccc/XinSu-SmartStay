"""facekit —— K1 端「身份证照 vs 现场抓拍」1:1 人脸比对工具包。

流水线：检测框 + 5 点关键点 → 相似变换对齐到 112x112 → ArcFace 128 维特征
→ L2 归一化 → 余弦相似度 → 双阈值 + 多帧聚合。
"""

from .align import ARC_TEMPLATE_112, align_face, similarity_transform
from .config import Config
from .detector import DetectedFace, YoloV5FaceDetector, YuNetDetector, build_detector
from .embedder import ArcFaceEmbedder
from .matcher import Decision, cosine, decide
from .pipeline import FaceVerifier, VerifyResult
from .quality import QualityReport, assess_quality

__all__ = [
    "ARC_TEMPLATE_112",
    "align_face",
    "similarity_transform",
    "Config",
    "DetectedFace",
    "YuNetDetector",
    "YoloV5FaceDetector",
    "build_detector",
    "ArcFaceEmbedder",
    "Decision",
    "cosine",
    "decide",
    "FaceVerifier",
    "VerifyResult",
    "QualityReport",
    "assess_quality",
]

__version__ = "0.1.0"
