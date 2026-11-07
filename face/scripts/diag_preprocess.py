"""诊断：为什么同人分数低于异人？

排查三个变量：通道顺序（RGB/BGR）、现场图光照（原图/提亮/CLAHE）、归一化方式。
用「同人分 - 异人分」的间隔来评判哪种配置判别力最好。
"""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.align import align_face
from facekit.config import Config
from facekit.io_utils import imread_unicode
from facekit.matcher import cosine
from facekit.pipeline import FaceVerifier

cfg = Config.load("config.yaml")
det = FaceVerifier(cfg).detector

import onnxruntime as ort

so = ort.SessionOptions()
so.log_severity_level = 3
sess = ort.InferenceSession("models/arcface_mobilefacenet_cut.q.onnx", so,
                            providers=["CPUExecutionProvider"])
inp = sess.get_inputs()[0].name


def embed(aligned, order="rgb", mean_std=True):
    x = aligned.astype(np.float32)
    x = x[:, :, ::-1] if order == "rgb" else x
    x = x / 255.0
    x = (x - 0.5) / 0.5 if mean_std else (x - 127.5) / 128.0
    x = np.transpose(x, (2, 0, 1))[None]
    e = sess.run(None, {inp: x})[0][0]
    return e / np.linalg.norm(e)


def prep(path):
    img = imread_unicode(path)
    f = det.detect(img)[0]
    return align_face(img, f.kps, 112)[0]


live = prep("samples/webcam_live.jpg")
kjw = prep(r"E:\人脸配对\kjw.jpg")
kjwsf = prep(r"E:\人脸配对\kjwsf.jpg")
sf = prep(r"E:\人脸配对\sf.jpg")

live_variants = {
    "原图": live,
    "gamma0.5(提亮)": np.clip(((live / 255.0) ** 0.5) * 255, 0, 255).astype(np.uint8),
    "gamma1.6(压暗)": np.clip(((live / 255.0) ** 1.6) * 255, 0, 255).astype(np.uint8),
    "CLAHE": None,
}
lab = cv2.cvtColor(live, cv2.COLOR_BGR2LAB)
lab[:, :, 0] = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(4, 4)).apply(lab[:, :, 0])
live_variants["CLAHE"] = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

print(f"{'配置':<26}{'同人kjw':>9}{'同人kjwS':>10}{'异人sf':>9}{'间隔':>9}")
for order in ("rgb", "bgr"):
    for name, img in live_variants.items():
        e_live = embed(img, order)
        s1 = cosine(embed(kjw, order), e_live)
        s2 = cosine(embed(kjwsf, order), e_live)
        s3 = cosine(embed(sf, order), e_live)
        gap = min(s1, s2) - s3
        print(f"{order+'/'+name:<26}{s1:>9.3f}{s2:>10.3f}{s3:>9.3f}{gap:>9.3f}")
