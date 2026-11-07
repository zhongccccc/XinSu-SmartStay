"""分别检查证件照与现场照能否检出人脸。"""
import glob
import os
import sys

import cv2

sys.path.insert(0, '/opt/zhikong/face')
from facekit.yunet_ort import YuNetORTDetector

det = YuNetORTDetector('/opt/zhikong/face/models/face_detection_yunet_2023mar.onnx')

ids = sorted(glob.glob('/opt/zhikong/data/idphotos/*.jpg'), key=os.path.getmtime)
lives = sorted(glob.glob('/opt/zhikong/data/photos/face_*.jpg'), key=os.path.getmtime)

for label, path in [('证件照', ids[-1] if ids else None),
                    ('现场照', lives[-1] if lives else None)]:
    if not path:
        print(label, '没有文件')
        continue
    img = cv2.imread(path)
    if img is None:
        print(label, '读不到', path)
        continue
    faces = det.detect(img)
    print('%s %s  %dx%d  检出 %d 张' % (label, os.path.basename(path), img.shape[1], img.shape[0], len(faces)))
    for f in faces[:2]:
        b = f.box
        print('   score=%.3f 框宽=%dpx' % (f.score, b[2] - b[0]))

# 统计现场照的检出率
print()
hit = 0
for p in lives[-10:]:
    img = cv2.imread(p)
    if img is None:
        continue
    n = len(det.detect(img))
    hit += (1 if n else 0)
print('最近 %d 张现场照中，能检出人脸的: %d 张' % (min(len(lives), 10), hit))
