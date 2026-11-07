#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按手册测试 IMX219 取帧：spacemitsrc 管线优先，回退 v4l2:/dev/video50。"""
import os
import time

import cv2

print("OpenCV:", cv2.__version__)
info = cv2.getBuildInformation()
for line in info.splitlines():
    if "GStreamer" in line or "V4L" in line:
        print("  ", line.strip())

CFG = "/usr/share/camera_json/csi3_camera_auto.json"
print("config exists:", os.path.exists(CFG))

PIPELINES = [
    ("spacemitsrc-1080", "spacemitsrc location=%s close-dmabuf=1 ! "
                         "video/x-raw,format=NV12,width=1920,height=1080 ! "
                         "videoconvert ! video/x-raw,format=BGR ! "
                         "appsink drop=true max-buffers=1 sync=false" % CFG),
    ("spacemitsrc-native", "spacemitsrc location=%s close-dmabuf=1 ! "
                           "videoconvert ! video/x-raw,format=BGR ! "
                           "appsink drop=true max-buffers=1 sync=false" % CFG),
]

for name, pipe in PIPELINES:
    print("\n--- %s ---" % name)
    t0 = time.time()
    cap = cv2.VideoCapture(pipe, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print("  打开失败(%.1fs)" % (time.time() - t0))
        cap.release()
        continue
    frame = None
    for i in range(30):
        ok, img = cap.read()
        if ok and img is not None:
            frame = img
        if time.time() - t0 > 8:
            break
    cap.release()
    if frame is None:
        print("  无帧(%.1fs)" % (time.time() - t0))
        continue
    out = "/tmp/cam_%s.jpg" % name
    cv2.imwrite(out, frame)
    print("  成功 %dx%d  %.1fs -> %s" % (frame.shape[1], frame.shape[0], time.time() - t0, out))
    print("  均值=%.1f 标准差=%.1f（均值过低=全黑，标准差过低=纯色）"
          % (frame.mean(), frame.std()))
    break
else:
    print("\n=== 回退 CAP_V4L2 /dev/video50 ===")
    cap = cv2.VideoCapture("/dev/video50", cv2.CAP_V4L2)
    print("opened:", cap.isOpened())
    if cap.isOpened():
        for i in range(10):
            ok, img = cap.read()
            if ok and img is not None:
                cv2.imwrite("/tmp/cam_v4l2.jpg", img)
                print("  成功 %dx%d -> /tmp/cam_v4l2.jpg" % (img.shape[1], img.shape[0]))
                break
        else:
            print("  v4l2 无帧")
    cap.release()
