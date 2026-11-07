"""拆解耗时：证件照 vs 现场帧，分别测检测与特征。"""
import glob
import os
import sys
import time

import cv2

sys.path.insert(0, '/opt/zhikong/face')
from facekit.config import Config
from facekit.pipeline import FaceVerifier

cfg = Config.load('/opt/zhikong/face/config.yaml')
v = FaceVerifier(cfg)

ids = sorted(glob.glob('/opt/zhikong/data/idphotos/*.jpg'), key=os.path.getmtime)
lives = sorted(glob.glob('/opt/zhikong/data/photos/face_*.jpg'), key=os.path.getmtime)[-3:]

id_img = cv2.imread(ids[-1])
h, w = id_img.shape[:2]
if min(h, w) < 240:
    f = 400.0 / min(h, w)
    id_img = cv2.resize(id_img, (int(w * f), int(h * f)), interpolation=cv2.INTER_CUBIC)

frames = [cv2.imread(p) for p in lives]
print('证件照 %dx%d，现场帧 %d 张' % (id_img.shape[1], id_img.shape[0], len(frames)))

t0 = time.time(); v.embed_id_photo(id_img); t1 = time.time()
print('证件照检测+特征: %.0f ms' % ((t1 - t0) * 1000))

for i, fr in enumerate(frames):
    t = time.time(); faces = v.detector.detect(fr); d = (time.time() - t) * 1000
    tag = '检出%d' % len(faces) if faces else '未检出'
    print('  帧%d 检测: %.0f ms  %s' % (i, d, tag))

    if faces:
        t = time.time(); v._extract(fr, gate=True); e = (time.time() - t) * 1000
        print('  帧%d 检测+对齐+特征: %.0f ms' % (i, e))

t = time.time(); r = v.verify(id_img, frames); total = (time.time() - t) * 1000
print('完整 verify(): %.0f ms  结论=%s 分数=%.3f' % (total, r.decision, r.score))
