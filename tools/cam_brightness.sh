#!/bin/bash
B=http://127.0.0.1:8080
curl -s -m 6 -o /tmp/s1.jpg $B/api/camera/snapshot.jpg
ls -l /tmp/s1.jpg
echo 123456 | sudo -S -p '' python3 - <<'PY'
import cv2
img = cv2.imread('/tmp/s1.jpg')
print("shape:", None if img is None else img.shape)
if img is not None:
    print("mean=%.1f std=%.1f min=%d max=%d" % (img.mean(), img.std(), img.min(), img.max()))
PY
echo "--- camera log ---"
grep -E "\[camera\]" /opt/zhikong/logs/backend.out | tail -5
