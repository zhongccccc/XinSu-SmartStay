#!/bin/bash
cd /opt/zhikong/app || exit 1
python3 -m py_compile backend/devices/face_local.py && echo "COMPILE_OK"
python3 - <<'PY'
import sys
sys.path.insert(0, '/opt/zhikong/face')
from facekit.pipeline import FaceVerifier
print('verify_fast 可用:', hasattr(FaceVerifier, 'verify_fast'))
PY
echo "=== 加速前后对比（用已保存的证件照与现场帧）==="
python3 - <<'PY'
import glob, os, sys, time
import cv2
sys.path.insert(0, '/opt/zhikong/face')
from facekit.config import Config
from facekit.pipeline import FaceVerifier

v = FaceVerifier(Config.load('/opt/zhikong/face/config.yaml'))
ids = sorted(glob.glob('/opt/zhikong/data/idphotos/*.jpg'), key=os.path.getmtime)
lives = sorted(glob.glob('/opt/zhikong/data/photos/face_*.jpg'), key=os.path.getmtime)[-3:]

idb = cv2.imread(ids[-1]); h, w = idb.shape[:2]
if min(h, w) < 240:
    f = 400.0 / min(h, w)
    idb = cv2.resize(idb, (int(w*f), int(h*f)), interpolation=cv2.INTER_CUBIC)
frames = [cv2.imread(p) for p in lives]

for name, fn in (('verify     ', v.verify), ('verify_fast', v.verify_fast)):
    t = time.time(); r = fn(idb, frames); ms = (time.time()-t)*1000
    print('  %s %.0f ms  结论=%s 分数=%.3f' % (name, ms, r.decision, r.score))
PY
