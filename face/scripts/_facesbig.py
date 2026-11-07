"""把两个人脸放大并排，肉眼确认到底是不是同一个人。"""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.align import align_face
from facekit.config import Config
from facekit.io_utils import imread_unicode, imwrite_unicode
from facekit.pipeline import FaceVerifier

cfg = Config.load("config.yaml")
det = FaceVerifier(cfg).detector

items = [
    ("kjw", r"E:\人脸配对\kjw.jpg"),
    ("kjwsf", r"E:\人脸配对\kjwsf.jpg"),
    ("live", "samples/webcam_live.jpg"),
    ("sf", r"E:\人脸配对\sf.jpg"),
]
tiles = []
for name, p in items:
    img = imread_unicode(p)
    f = det.detect(img)[0]
    a, _, _ = align_face(img, f.kps, 112)
    big = cv2.resize(a, (256, 256), interpolation=cv2.INTER_CUBIC)
    cv2.putText(big, name, (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    tiles.append(big)

imwrite_unicode("out/faces_big.jpg", cv2.hconcat(tiles))
print("saved out/faces_big.jpg")
