"""同一组图，分别用 FP32 / INT8 模型算相似度，看量化损失了多少判别力。"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.align import align_face
from facekit.config import Config
from facekit.embedder import ArcFaceEmbedder
from facekit.io_utils import imread_unicode
from facekit.matcher import cosine
from facekit.pipeline import FaceVerifier

paths = {
    "sf(男)": r"E:\人脸配对\sf.jpg",
    "kjw": r"E:\人脸配对\kjw.jpg",
    "kjwsf": r"E:\人脸配对\kjwsf.jpg",
    "live(kjw)": "samples/webcam_live.jpg",
}

cfg = Config.load("config.yaml")
det = FaceVerifier(cfg).detector

# 对齐一次，两种模型共用同一批 112x112
aligned = {}
for name, p in paths.items():
    img = imread_unicode(p)
    faces = det.detect(img)
    a, _, err = align_face(img, faces[0].kps, 112)
    aligned[name] = a
    print(f"{name:10s} align_err={err:.2f}")

for tag, model in (("INT8 q", "models/arcface_mobilefacenet_cut.q.onnx"),
                   ("FP32  ", "models/arcface_mobilefacenet_cut.onnx")):
    emb = ArcFaceEmbedder(model, providers=["CPUExecutionProvider"], num_threads=4)
    E = {k: emb.embed(v) for k, v in aligned.items()}
    print(f"\n=== {tag} ===")
    names = list(E)
    print(" " * 11 + "".join(f"{n:>11s}" for n in names))
    for a in names:
        print(f"{a:10s} " + "".join(f"{cosine(E[a], E[b]):>11.3f}" for b in names))
    print(f"  同人(kjw vs live) = {cosine(E['kjw'], E['live(kjw)']):.3f}")
    print(f"  同人(kjwsf vs live) = {cosine(E['kjwsf'], E['live(kjw)']):.3f}")
    print(f"  异人(sf vs live)  = {cosine(E['sf(男)'], E['live(kjw)']):.3f}")
    print(f"  异人(sf vs kjw)   = {cosine(E['sf(男)'], E['kjw']):.3f}")
