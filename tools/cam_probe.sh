#!/bin/bash
echo "=== media-ctl ==="
which media-ctl && media-ctl -p -d /dev/media0 2>&1 | head -45
echo
echo "=== v4l2 formats per node ==="
for d in /dev/video1 /dev/video2 /dev/video3; do
  echo "--- $d"; timeout 5 v4l2-ctl -d $d --list-formats 2>&1 | head -8
done
echo "=== try capture on ccic nodes ==="
for d in /dev/video1 /dev/video2 /dev/video3; do
  echo "--- $d"
  timeout 6 v4l2-ctl -d $d --stream-mmap --stream-count=1 --stream-to=/tmp/f_$(basename $d).bin 2>&1 | tail -2
  ls -l /tmp/f_$(basename $d).bin 2>/dev/null
done
echo "=== sysfs input caps ==="
for e in /dev/input/event0 /dev/input/event3; do
  echo "--- $e"
  ls /sys/class/input/$(basename $e)/device/capabilities/ 2>&1
  echo -n "abs="; cat /sys/class/input/$(basename $e)/device/capabilities/abs 2>/dev/null; echo
  echo -n "name="; cat /sys/class/input/$(basename $e)/device/name 2>/dev/null; echo
done
echo "=== python cv2 probe (manual) ==="
python3 - <<'PY'
import glob, time
import cv2
for p in sorted(glob.glob('/dev/video*')):
    try:
        cap = cv2.VideoCapture(p, cv2.CAP_V4L2)
        if not cap.isOpened():
            print(p, 'open-fail'); cap.release(); continue
        ok, fr = cap.read()
        print(p, 'opened ok=%s shape=%s' % (ok, None if fr is None else fr.shape))
        cap.release()
    except Exception as e:
        print(p, 'err', e)
PY
