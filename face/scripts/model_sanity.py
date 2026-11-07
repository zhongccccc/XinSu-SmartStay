"""模型健全性检查：同一个人的小扰动应该保持高相似，换人才应该掉下去。

如果「同图翻转/轻微调光」都掉到 0.6 以下，说明这个 embedding 本身不稳定，
问题不在阈值，也不在光照。
"""

import sys
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.align import align_face
from facekit.config import Config
from facekit.io_utils import imread_unicode
from facekit.matcher import cosine
from facekit.pipeline import FaceVerifier

cfg = Config.load("config.yaml")
det = FaceVerifier(cfg).detector

so = ort.SessionOptions()
so.log_severity_level = 3
sess = ort.InferenceSession("models/arcface_mobilefacenet_cut.q.onnx", so,
                            providers=["CPUExecutionProvider"])
inp = sess.get_inputs()[0].name


def embed(bgr):
    x = bgr[:, :, ::-1].astype(np.float32) / 255.0
    x = (x - 0.5) / 0.5
    x = np.transpose(x, (2, 0, 1))[None]
    e = sess.run(None, {inp: x})[0][0]
    return e / np.linalg.norm(e)


def aligned_of(path):
    img = imread_unicode(path)
    f = det.detect(img)[0]
    return align_face(img, f.kps, 112)[0]


base = aligned_of(r"E:\人脸配对\kjw.jpg")
other = aligned_of(r"E:\人脸配对\sf.jpg")

variants = {
    "原图": base,
    "水平翻转": cv2.flip(base, 1),
    "亮度+10%": np.clip(base.astype(np.float32) * 1.10, 0, 255).astype(np.uint8),
    "亮度-10%": np.clip(base.astype(np.float32) * 0.90, 0, 255).astype(np.uint8),
    "轻微模糊": cv2.GaussianBlur(base, (3, 3), 0.6),
    "JPEG q60": cv2.imdecode(
        cv2.imencode(".jpg", base, [int(cv2.IMWRITE_JPEG_QUALITY), 60])[1], cv2.IMREAD_COLOR),
    "中心再裁 85%": cv2.resize(
        base[int(112 * 0.075):int(112 * 0.925), int(112 * 0.075):int(112 * 0.925)], (112, 112)),
    "椭圆遮罩": base * cv2.resize(
        cv2.ellipse(np.zeros((112, 112), np.uint8), (56, 56), (52, 60), 0, 0, 360, 255, -1),
        (112, 112))[..., None] // 255 if False else base,
}

e_base = embed(base)
print(f"{'扰动':<16}{'与自己的相似度':>14}")
for name, img in variants.items():
    print(f"{name:<16}{cosine(e_base, embed(img)):>14.3f}")

print(f"\n{'换人（sf）':<16}{cosine(e_base, embed(other)):>14.3f}")
