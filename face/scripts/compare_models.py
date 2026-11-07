"""用 buffalo_l 的 w600k_r50（512 维）重算同一组图，看能不能把同人/异人分开。"""

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

cfg = Config.load("config.yaml")
det = FaceVerifier(cfg).detector

paths = {
    "sf(男)": r"E:\人脸配对\sf.jpg",
    "kjw": r"E:\人脸配对\kjw.jpg",
    "kjwsf": r"E:\人脸配对\kjwsf.jpg",
    "live": "samples/webcam_live.jpg",
}

aligned = {}
for name, p in paths.items():
    img = imread_unicode(p)
    f = det.detect(img)[0]
    aligned[name] = align_face(img, f.kps, 112)[0]

for tag, model in (("MobileFaceNet 128", "models/arcface_mobilefacenet_cut.q.onnx"),
                   ("buffalo R50 512", "models/w600k_r50.q.onnx")):
    emb = ArcFaceEmbedder(model, providers=["CPUExecutionProvider"], num_threads=4)
    E = {k: emb.embed(v) for k, v in aligned.items()}
    print(f"\n=== {tag} ===")
    names = list(E)
    print(" " * 11 + "".join(f"{n:>11s}" for n in names))
    for a in names:
        print(f"{a:10s} " + "".join(f"{cosine(E[a], E[b]):>11.3f}" for b in names))
    same = max(cosine(E["kjw"], E["live"]), cosine(E["kjwsf"], E["live"]))
    imp = max(cosine(E["sf(男)"], E["live"]), cosine(E["sf(男)"], E["kjw"]))
    print(f"  同人最好 {same:.3f} / 异人最高 {imp:.3f} / 间隔 {same - imp:+.3f}")

import time

emb = ArcFaceEmbedder("models/w600k_r50.q.onnx", providers=["CPUExecutionProvider"], num_threads=4)
t0 = time.perf_counter()
for _ in range(20):
    emb.embed(aligned["kjw"])
print(f"\nR50 单次特征提取: {(time.perf_counter()-t0)/20*1000:.1f} ms (x86 CPU)")
