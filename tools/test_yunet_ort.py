"""在 K1 上用 ORT 版 YuNet 检测样例图，打印框、分数、5 点，验证解码正确。"""
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, '/opt/zhikong/face')
from facekit.yunet_ort import YuNetORTDetector

det = YuNetORTDetector('/opt/zhikong/face/models/face_detection_yunet_2023mar.onnx')

for name in ['samples/id_photo_sample.png', 'samples/live_sim.jpg', 'samples/webcam_live.jpg']:
    img = cv2.imread('/opt/zhikong/face/' + name)
    if img is None:
        print(name, '读不到')
        continue
    t0 = time.time()
    faces = det.detect(img)
    ms = (time.time() - t0) * 1000
    print('%s  %dx%d  耗时 %.0fms  检测到 %d 张' % (name, img.shape[1], img.shape[0], ms, len(faces)))
    for f in faces[:2]:
        b = f.box
        print('   score=%.3f  box=(%d,%d,%d,%d)  宽=%d' % (
            f.score, b[0], b[1], b[2], b[3], b[2] - b[0]))
        if f.kps is not None:
            pts = ', '.join('(%.0f,%.0f)' % (p[0], p[1]) for p in f.kps)
            # 瞳距：左眼(0) 到 右眼(1)
            d = float(np.hypot(*(f.kps[0] - f.kps[1])))
            print('   5点: %s  瞳距=%.0fpx' % (pts, d))
